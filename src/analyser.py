import mne
from pathlib import Path
import respiration as resp
from master import recordings
import numpy as np

class MEG_participant:
    def __init__(self, id, meg_date, mr_date, bad_channels = [], project_path = Path("/projects/MINDLAB2021_MEG-CerebellarClock-FuncSig")):
        self.id = id
        self.meg_date = meg_date
        self.mr_date = mr_date
        self.project_path = project_path
        self.fnames = {}

    def populate_fnames(self, mkdirs = True):
        self.fnames["raw"] =  self.project_path / "raw"
        self.fnames["scratch"] =  self.project_path / "scratch"
        self.fnames["MEG"] =  self.fnames["scratch"] / "MEG"
        self.fnames["behav"] = self.fnames["scratch"] / "behavioural_data"
        self.fnames["fig"] =  Path(__file__).parents[1] / "fig" / f"{self.id}"
        self.fnames["subjects_dir"] = self.fnames["scratch"] / "freesurfer"
        self.fnames["events"] = self.fnames["MEG"] / f"{self.id}" / f"{self.meg_date}" / "fc-eve.fif"
        self.fnames["resp"] = self.fnames["scratch"] / "respiration" / f"{self.id}"

        self.fnames["phase_angles"] = self.fnames["resp"] / f"{self.id}_phase_angles_events.csv"

        files_with_number = list((self.fnames["raw"] / self.id / self.meg_date / "MEG").rglob("*raw_[0-9].fif"))
        files_without_number = list((self.fnames["raw"] / self.id / self.meg_date / "MEG").rglob("*raw.fif"))
        self.fnames["subj_raws_list"] = sorted(files_with_number + files_without_number)

        if mkdirs:
            for name, path in self.fnames.items():
                if name.endswith("_list") or "." in str(path): # not turning files into dirs
                    continue
                if not path.exists():
                    path.mkdir(parents = True)

        
    def load_raw(self, preload = False):
        # NOTE: make sure to update code to take into account the different head positions!
        raws = []
        for fname in self.fnames["subj_raws_list"]:
            raws.append(mne.io.read_raw_fif(fname, preload = preload))
            
        self.raw = mne.concatenate_raws(raws)
        
    def load_events(self):
        self.events = mne.read_events(self.fnames["events"])
        print(self.events[:, 0])
        print(f"number unique {len(np.unique(self.events[:, 0]))}, total length = {len(self.events[:, 0])})")

    def extract_resp_angle(self):        
        # check if raw is loaded, if not:
        if not self.raw.preload: # only load the respiratory channel
            resp_ts = self.raw.copy().pick("MISC001")
            resp_ts.load_data()
        
        else: # get the respiration data
            resp_ts = self.raw.copy().pick("MISC001")

        resp_ts = resp_ts.filter(None, 1, picks = "MISC001")
        resp_ts, tmp_events = resp_ts.resample(100, events = self.events) # resampling the events at the same time!

        resp_ts = resp_ts.get_data().squeeze() # squeeze to get rid of the channel dimension
        normalised_ts, peaks, troughs, phase_angle = resp.extract_phase_angle(resp_ts, widths=25, min_sample = 50)

        df = resp.phase_angle_events(phase_angle, tmp_events)

        df.to_csv(self.fnames["phase_angles"], index = False)

        # maybe also save the phase vector!
        
        resp.sanity_check_phase_angle(resp_timeseries = None, normalised_ts = normalised_ts, peaks = peaks, troughs = troughs, phase_angle = None, savepath = self.fnames["fig"] / f"{self.id}_respiration.png")
        resp.summary_plots(peaks, troughs, phase_angle, savepath = self.fnames["fig"] / f"{self.id}_respiration_summary.png" )



if __name__ in "__main__":
    #sub = dict(subject='0031', date='20210825_000000', mr_date='20210820_094714') # subject without
    #sub = dict(subject='0006', date='20210728_000000', mr_date='20210811_173642') # subject with split files -> currently giving error due to different 'dev_head_t'
    
    for sub in recordings[3:4]:

        participant = MEG_participant(id = sub["subject"], meg_date = sub["date"], mr_date = sub["mr_date"])
        participant.populate_fnames()
        participant.load_events()
        participant.load_raw(preload = False)
        participant.extract_resp_angle()




    


