- main.py has code which runs the GUI which allows users to add youtube video clips for training clips. 
The GUI adds the clips to the exercise_training_clips.json, while the code below it processes the json and adds it to the angles_trial.csv (features csv file) 
as well as labels.csv (labels csv file) which are both located in the 'archive_time_series/' directory

- model_time_series.py uses angles_trial.csv and labels.csv to train the model

- my_ts_model.keras is the exported model which is used when classifying

- exercise_training_clips.json is the json which maps exercises to their associated training clips which have the video link, the start_time and end_time of the clip