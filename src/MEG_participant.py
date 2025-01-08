import mne
from mne.minimum_norm import apply_inverse, make_inverse_operator
from pathlib import Path
import respiration as resp


class MEG_participant:
    def __init__(self, subj_id, meg_date, mr_date, bad_channels = [], run_path = Path("."),  project_path = Path("/projects/MINDLAB2021_MEG-CerebellarClock-FuncSig")):
        self.subj_id = subj_id
        self.bad_channels = bad_channels
        self.meg_date = meg_date
        self.mr_date = mr_date
        self.project_path = project_path
        self.run_path = run_path
        self.fnames = {}

    def populate_fnames(self, mkdirs = True):
        self.fnames["raw"] =  self.project_path / "raw"
        self.fnames["scratch"] =  self.project_path / "scratch"
        self.fnames["MEG"] =  self.fnames["scratch"] / "MEG"
        self.fnames["behav"] = self.fnames["scratch"] / "behavioural_data"
        self.fnames["fig"] =  self.run_path / "fig" / self.subj_id
        self.fnames["subjects_dir"] = self.fnames["scratch"] / "freesurfer"
        self.fnames["events"] = self.fnames["MEG"] / self.subj_id / self.meg_date / "fc-eve.fif"
        self.fnames["resp"] = self.fnames["scratch"] / "respiration" / self.subj_id
        self.fnames["subj_freesurfer"] = self.fnames["scratch"] / "freesurfer" / self.subj_id
        self.fnames["subj_bem"] = self.fnames["subj_freesurfer"] / "bem"
        self.fnames["phase_angles"] = self.fnames["resp"] / f"{self.subj_id}_phase_angles_events.csv"

        files_with_number = list((self.fnames["raw"] / self.subj_id / self.meg_date / "MEG").rglob("*raw_[0-9].fif"))
        files_without_number = list((self.fnames["raw"] / self.subj_id / self.meg_date / "MEG").rglob("*raw.fif"))
        self.fnames["subj_raws_list"] = sorted(files_with_number + files_without_number)

        if mkdirs:
            for name, path in self.fnames.items():
                if name.endswith("_list") or "." in str(path): # not turning files into dirs
                    continue
                if not path.exists():
                    path.mkdir(parents = True)

        
    def load_raw(self, preload = False):
        raws = []
        for fname in self.fnames["subj_raws_list"]:
            raws.append(mne.io.read_raw_fif(fname, preload = preload))
            
        self.raw = mne.concatenate_raws(raws)

    def filter_raw(self, h_freq = 40, l_freq = None):
        self.raw = self.raw.filter(l_freq = l_freq, h_freq = h_freq)
        
    def load_events(self):
        self.events = mne.read_events(self.fnames["events"])

    def create_epochs(self, event_id, tmin = -0.2, tmax = 1, baseline = (None, 0)):
        # Picks MEG channels
        picks = mne.pick_types(
            self.raw.info, meg=True, eeg=False, eog=True, stim=False, exclude=self.bad_channels
        )
        
        reject = dict(grad=4000e-13, mag=4e-12, eog=150e-6)

        # Load epochs
        self.epochs = mne.Epochs(
            self.raw,
            self.events,
            event_id,
            tmin,
            tmax,
            picks=picks,
            baseline=baseline,
            reject=reject,
            preload=True,
        )

    def epochs_extract_power_sourcespace(self, labels = ['Cerebelum_Crus1_R'], freqs =):

        inverse_operator = make_inverse_operator(self.raw.info, fwd, noise_cov, depth=None, loose=loose, verbose=True)
        
        labels_power = mne.norm.source_induced_power(
            epochs,
            inverse_operator,
            freqs,
            labels,
            baseline=(-0.1, 0),
            baseline_mode="mean",
            n_cycles=n_cycles,
            n_jobs=None,
            return_plv=False,
        )
        pass

    def extract_resp_angle(self):        
        # check if raw is loaded, if not:
        if not self.raw.preload: # only load the respiratory channel
            resp_ts = self.raw.copy().pick("MISC001")
            resp_ts.load_data()
        
        else: # get the respiration data
            resp_ts = self.raw.copy().pick("MISC001")

        resp_ts = resp_ts.filter(None, 1, picks = "MISC001")
        #resp_ts, tmp_events = resp_ts.resample(100, events = self.events) # resampling the events at the same time!

        resp_ts = resp_ts.get_data().squeeze() # squeeze to get rid of the channel dimension
        normalised_ts, peaks, troughs, phase_angle = resp.extract_phase_angle(resp_ts, widths=250, min_sample = 50)


        df = resp.phase_angle_events(phase_angle, self.events)

        df.to_csv(self.fnames["phase_angles"], index = False)

        # NOTE: maybe also save the phase vector!
        
        resp.sanity_check_phase_angle(resp_timeseries = None, normalised_ts = normalised_ts, peaks = peaks, troughs = troughs, phase_angle = phase_angle, savepath = self.fnames["fig"] / f"{self.subj_id}_respiration.png")
        resp.summary_plots(peaks, troughs, phase_angle, savepath = self.fnames["fig"] / f"{self.subj_id}_respiration_summary.png" )






