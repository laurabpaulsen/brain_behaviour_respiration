from config import recordings, event_ids
import sys
sys.path.append("src")
from MEG_participant import MEG_participant
from pathlib import Path

def determine_project_path():
    pass


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

    for sub in recordings[4:5]:
        print(sub)

        participant = MEG_participant(
            subj_id = sub["subject"], 
            meg_date = sub["date"], 
            mr_date = sub["mr_date"], 
            bad_channels = sub["bad_channels"],
            run_path = Path(__file__).parents[1]
            )
        
        participant.populate_fnames()
        participant.load_events()
        participant.load_raw(preload = False)
        participant.filter_raw(8, 13) # alpha band
        participant.create_epochs(event_id=event_ids)
        #participant.epochs_extract_power_sourcespace(labels=ROI)
        # participant.extract_resp_angle()