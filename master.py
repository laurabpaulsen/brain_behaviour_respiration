from config import recordings, event_ids
import sys
sys.path.append("src")
from MEG_participant import MEG_participant
from pathlib import Path
import pickle as pkl

def determine_project_path():
    pass


def get_resp_data(participant, l_freq = None, h_freq = 10, sample_rate = 300):
    resp_ts = participant.raw.copy().pick("MISC001")
    resp_ts.load_data()


    resp_ts = resp_ts.filter(l_freq, h_freq, picks = "MISC001", n_jobs = participant.n_jobs)
    resp_ts, tmp_events = resp_ts.resample(sample_rate, events = participant.events) # resampling the events at the same time!

    first_sample = resp_ts.first_samp

    tmp_events[:, 0] = tmp_events[:, 0]-first_sample

    data = {"respiration_timeseries": resp_ts, "events": tmp_events}
    
    print(participant.project_path)
    print(participant.subj_id)
    output_path = Path(participant.project_path) / "scratch" / "resp_data_MH" / f"{participant.subj_id}.pkl"

    
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)


    with output_path.open("wb") as f:
        pkl.dump(data, f)



if __name__ in "__main__":

    ROI = ['Cerebelum_Crus1_L',
         'Cerebelum_Crus1_R',
         'Cerebelum_Crus2_L',
         'Cerebelum_Crus2_R',
         'Cerebelum_3_L',
         'Cerebelum_3_R',
         'Cerebelum_4_5_L',
         'Cerebelum_4_5_R',
         'Cerebelum_6_L',
         'Cerebelum_6_R',
         'Cerebelum_7b_L',
         'Cerebelum_7b_R',
         'Cerebelum_8_L',
         'Cerebelum_8_R',
         'Cerebelum_9_L',
         'Cerebelum_9_R',
         'Cerebelum_10_L',
         'Cerebelum_10_R']

    for sub in recordings:
        print("\n\n\n", sub)

        participant = MEG_participant(
            subj_id = sub["subject"], 
            meg_date = sub["date"], 
            mr_date = sub["mr_date"], 
            bad_channels = sub["bad_channels"],
            run_path = Path(__file__).parents[1],
            event_ids = event_ids,
            n_jobs = 4
            )
        
        participant.populate_fnames()
        participant.load_events()
        participant.load_raw(preload = False)
        get_resp_data(participant)

        #participant.filter_raw(8, 13) # alpha band
        #participant.create_epochs(event_id=event_ids)
        #participant.epochs_extract_power_sourcespace(labels=ROI)
        #participant.extract_resp_angle()