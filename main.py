import json
import os
import cv2
import mediapipe as mp
import numpy as np
from pytube import YouTube
from helpers import convert_into_numeric_pairs, new_pairs_2, convert_angle
import pandas as pd
import tkinter as tk
from tkinter import ttk
import re
from ttkthemes import ThemedStyle  # Import ThemedStyle from ttkthemes
import customtkinter


entries_list = []


def download_youtube_video(url, output_path, num):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    stream.download(output_path)
    video_filename = stream.default_filename #+ "_" + str(num)
    return video_filename

def extract_clip(input_video, start_time, end_time, video_folder, output_folder, num):
    cap = cv2.VideoCapture(video_folder+input_video)
    print("Done")
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    start_frame = int(start_time * frame_rate)
    end_frame = int(end_time * frame_rate)

    output_filename_template = os.path.join(output_folder, "frame_{:04d}.jpg")
    frame_number = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number >= start_frame and frame_number <= end_frame:
            output_filename = output_filename_template.format(frame_number)
            cv2.imwrite(output_filename, frame)

        if frame_number > end_frame:
            break

        frame_number += 1

    cap.release()

def process_frames(image_path, vid_id, frame_order):
    with mp_holistic.Holistic(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            refine_face_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
    ) as holistic:
        # print(image_path)
        frame = cv2.imread(image_path)

        image_height, image_width, _ = frame.shape
        results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        annotated_image = frame.copy()

        if results.segmentation_mask is not None:
            condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
            bg_image = np.zeros(frame.shape, dtype=np.uint8)
            bg_image[:] = BG_COLOR
            annotated_image = np.where(condition, annotated_image, bg_image)

        # Draw pose, face, and hand landmarks on the image
        mp_drawing.draw_landmarks(
            annotated_image,
            results.face_landmarks,
            mp_holistic.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
        )
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
        )

        if results.pose_landmarks is not None:
            # X = []
            # my_dict = {}
            # angles = []
            # for pair in new_pairs_2:
            #     angle = convert_angle(results.pose_landmarks.landmark, pair)
            #     angles.append(angle)
            #     my_dict[str(pair)] = angle

            # frame_filename = f"frame_{num}.png"
            # frame_filepath = os.path.join(destination_directory, frame_filename)
            # cv2.imwrite(frame_filepath, annotated_image)

            # print("Image #:", num)
            X = []
            new_row_data = []
            new_row_data.append(vid_id)
            new_row_data.append(frame_order)
            for pair in new_pairs_2:
                angle = convert_angle(results.pose_landmarks.landmark, pair)
                new_row_data.append(angle)
            # Calculate and append the nose y-coordinate/left knee y-coordinate ratio
            if results.pose_landmarks.landmark[0].y != 0 and results.pose_landmarks.landmark[25].y != 0:
                ratio = results.pose_landmarks.landmark[0].y / results.pose_landmarks.landmark[25].y
                new_row_data.append(ratio)
            
            
            # print(new_row_data)

            features_cont.loc[len(features_cont)] = new_row_data


# Version 0 of function. (Not in use)
def clip_manager_gui_0():
    # Function to save the JSON data to a file
    def save_json_data(file_path):
        with open(file_path, "w") as f:
            json.dump(exercise_clip_data, f, indent=4)
    def add_video():
        exercise_name = exercise_name_entry.get().strip()
        video_link = video_link_entry.get().strip()
        start_timestamp = start_timestamp_entry.get().strip()
        end_timestamp = end_timestamp_entry.get().strip()

        if not exercise_name or not video_link or not start_timestamp or not end_timestamp:
            status_label.config(text="Please fill in all fields.", foreground="red")  # Use "foreground" instead of "-fg"
            return

        if exercise_name not in exercise_clip_data:
            exercise_clip_data[exercise_name] = []

        # Check if start_timestamp and end_timestamp are valid (format: "MM:SS")
        if not valid_timestamp_format(start_timestamp) or not valid_timestamp_format(end_timestamp):
            status_label.config(text="Invalid timestamp format. Use MM:SS.", foreground="red")  # Use "foreground" instead of "-fg"
            return

        exercise_clip_data[exercise_name].append({
            "link": video_link,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp
        })

        # Clear input fields
        exercise_name_entry.delete(0, tk.END)
        video_link_entry.delete(0, tk.END)
        start_timestamp_entry.delete(0, tk.END)
        end_timestamp_entry.delete(0, tk.END)

        status_label.config(text="Video added successfully!", foreground="green")  # Use "foreground" instead of "-fg"

        # Update the video list
        update_video_list()
        save_json_data(exercise_clips_file_path)
    def delete_video():
        selected_items = video_tree.selection()
        for item in selected_items:
            # exercise = video_tree.item(item, "text")
            exercise = video_tree.item(item, "values")[0]
            link = video_tree.item(item, "values")[1]
            print(exercise, link)

            # Remove the selected clip from the Treeview
            video_tree.delete(item)

            # Remove the selected clip from the JSON data
            for video in exercise_clip_data[exercise]:
                if video["link"] == link:
                    exercise_clip_data[exercise].remove(video)
                    break
        status_label.config(text="Video deleted successfully!", foreground="red")  # Use "foreground" instead of "-fg"
        # Save the updated JSON data after deleting clips
        save_json_data(exercise_clips_file_path)
    def valid_timestamp_format(timestamp):
        # Check if the timestamp has the format "MM:SS"
        if not re.match(r"^\d{1,2}:\d{2}$", timestamp):
            return False

        # Additional checks for valid MM and SS values
        minutes, seconds = timestamp.split(":")
        if int(minutes) < 0 or int(minutes) >= 60 or int(seconds) < 0 or int(seconds) >= 60:
            return False

        return True

    def update_video_list():
        # video_list.delete(0, tk.END)

        # for exercise, videos in exercise_clip_data.items():
        #     if videos:
        #         for video in videos:
        #             video_list.insert(tk.END, f"{exercise} - {video['link']}")
        # Clear the existing items in the Treeview
        video_tree.delete(*video_tree.get_children())

        # Update the Treeview with the video links grouped under exercise names
        for exercise, videos in exercise_clip_data.items():
            for video in videos:
                video_tree.insert("", "end", values=(exercise, video["link"], video["start_timestamp"], video["end_timestamp"]))

    def treeview_sort_column(tree, col, reverse):
        # Helper function for sorting columns in the Treeview
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

    
    root = tk.Tk()  # Create a tk.Tk() instance

    # style = ThemedStyle(root)
    # style.set_theme("yaru")  # Choose a modern theme, e.g., "plastik"

    root.title("Exercise Video Manager")
    # Set the column and row configurations to expand and fill available space
    root.columnconfigure(0, weight=1)  # Column 0 will expand horizontally
    root.rowconfigure(1, weight=1)  # Row 7 (the Listbox) will expand vertically



    # Create GUI elements with the updated style

    # Labels
    exercise_name_label = ttk.Label(root, text="Exercise Name:")
    exercise_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    video_link_label = ttk.Label(root, text="Video Link:")
    video_link_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    start_timestamp_label = ttk.Label(root, text="Start Timestamp (MM:SS):")
    start_timestamp_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    end_timestamp_label = ttk.Label(root, text="End Timestamp (MM:SS):")
    end_timestamp_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    status_label = ttk.Label(root, text="", foreground="green")
    status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    video_list_label = ttk.Label(root, text="Video List")
    video_list_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Entry fields
    exercise_name_entry = ttk.Entry(root)
    exercise_name_entry.grid(row=0, column=1, padx=10, pady=10)

    video_link_entry = ttk.Entry(root)
    video_link_entry.grid(row=1, column=1, padx=10, pady=10)

    start_timestamp_entry = ttk.Entry(root)
    start_timestamp_entry.grid(row=2, column=1, padx=10, pady=10)

    end_timestamp_entry = ttk.Entry(root)
    end_timestamp_entry.grid(row=3, column=1, padx=10, pady=10)

    # Buttons
    add_button = ttk.Button(root, text="Add Video", command=add_video)
    add_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Create a Treeview to display the video list with subheadings
    video_tree = ttk.Treeview(root, columns=("Exercise", "Link", "Start Time", "End Time"), show="headings")
    video_tree.heading("Exercise", text="Exercise")
    video_tree.heading("Link", text="Link")
    video_tree.heading("Start Time", text="Start Time")
    video_tree.heading("End Time", text="End Time")

    # Insert data into the Treeview
    for exercise, videos in exercise_clip_data.items():
        for video in videos:
            video_tree.insert("", "end", values=(exercise, video["link"], video["start_timestamp"], video["end_timestamp"]))

    video_tree.grid(row=0, column=0, sticky="nsew")

    # Enable resizing the columns of the Treeview
    for col in ("Exercise", "Link", "Start Time", "End Time"):
        video_tree.column(col, anchor="center")
        video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    video_tree.grid(row=7, column=0, sticky="nsew", columnspan=2, padx=10, pady=10)

    # # Enable resizing the columns of the Treeview
    # for col in ("Link", "Start Time", "End Time"):
    #     video_tree.column(col, anchor="center")
    #     video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    
    # Enable resizing the columns of the Treeview
    for col in ("Exercise", "Link", "Start Time", "End Time"):
        video_tree.column(col, anchor="center")
        video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    # Create vertical scrollbar for the Treeview
    vsb = ttk.Scrollbar(root, orient="vertical", command=video_tree.yview)
    video_tree.configure(yscrollcommand=vsb.set)

    # Create the Delete button
    delete_button = ttk.Button(root, text="Delete", command=delete_video)
    delete_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    status_label = ttk.Label(root, text="", foreground="red")
    status_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10)



    # # Create a PanedWindow to hold the video_list and other widgets
    # paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
    # paned_window.grid(row=7, column=0, sticky="nsew", columnspan=2, padx=10, pady=10)

    # # Create the video_list (Listbox) and add it to the PanedWindow
    # video_list = tk.Listbox(paned_window)
    # paned_window.add(video_list)

    # # Listbox
    # video_list = tk.Listbox(root)
    # video_list.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    # Start with an initial video list
    update_video_list()

    # Run the main event loop
    root.mainloop()

def clip_manager_gui():
    # Function to save the JSON data to a file
    def save_json_data(file_path):
        with open(file_path, "w") as f:
            json.dump(exercise_clip_data, f, indent=4)
    def add_video():
        exercise_name = exercise_name_entry.get().strip()
        video_link = video_link_entry.get().strip()
        start_timestamp = start_timestamp_entry.get().strip()
        end_timestamp = end_timestamp_entry.get().strip()

        if not exercise_name or not video_link or not start_timestamp or not end_timestamp:
            status_label.configure(text="Please fill in all fields.", text_color="red")  # Use "foreground" instead of "-fg"
            return

        if exercise_name not in exercise_clip_data:
            exercise_clip_data[exercise_name] = []

        # Check if start_timestamp and end_timestamp are valid (format: "MM:SS")
        if not valid_timestamp_format(start_timestamp) or not valid_timestamp_format(end_timestamp):
            status_label.configure(text="Invalid timestamp format. Use MM:SS.", text_color="red")  # Use "foreground" instead of "-fg"
            return

        exercise_clip_data[exercise_name].append({
            "link": video_link,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp
        })

        # Clear input fields
        exercise_name_entry.delete(0, tk.END)
        video_link_entry.delete(0, tk.END)
        start_timestamp_entry.delete(0, tk.END)
        end_timestamp_entry.delete(0, tk.END)

        status_label.configure(text="Video added successfully!", text_color="green", font = ("Futura", 18))  # Use "foreground" instead of "-fg"

        # Update the video list
        update_video_list()
        save_json_data(exercise_clips_file_path)
    def delete_video():
        selected_items = video_tree.selection()
        for item in selected_items:
            # exercise = video_tree.item(item, "text")
            exercise = video_tree.item(item, "values")[0]
            link = video_tree.item(item, "values")[1]
            start_time = video_tree.item(item, "values")[2]
            end_time = video_tree.item(item, "values")[3]
            print(exercise, link, start_time, end_time)

            # Remove the selected clip from the Treeview
            video_tree.delete(item)

            # Remove the selected clip from the JSON data
            for video in exercise_clip_data[exercise]:
                if video["link"] == link and video["start_timestamp"] == start_time and video["end_timestamp"] == end_time:
                    exercise_clip_data[exercise].remove(video)
                    break
        status_label.configure(text="Video deleted successfully!", text_color="red", font = ("Futura", 18))  # Use "foreground" instead of "-fg"
        # Save the updated JSON data after deleting clips
        save_json_data(exercise_clips_file_path)
    def show_context_menu(event):
        selected_item = video_tree.identify_row(event.y)
        if selected_item:
            video_tree.selection_set(selected_item)
            right_click_menu.post(event.x_root, event.y_root)

    def optionmenu_callback(choice):
        selected_item = video_tree.selection()
        if selected_item:
            action = optionmenu_var.get()
            if action == "Edit":
                edit_clip()
            elif action == "Duplicate":
                duplicate_clip()

    def edit_clip():
        selected_item = video_tree.selection()
        if selected_item:
            # Get the values of the selected item
            values = video_tree.item(selected_item, "values")
            exercise_name_entry.delete(0, tk.END)
            video_link_entry.delete(0, tk.END)
            start_timestamp_entry.delete(0, tk.END)
            end_timestamp_entry.delete(0, tk.END)
            exercise_name_entry.insert(0, values[0])
            video_link_entry.insert(0, values[1])
            start_timestamp_entry.insert(0, values[2])
            end_timestamp_entry.insert(0, values[3])

            # Show the "Save" button and hide the "Add" button
            add_button.grid_remove()
            save_button.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

            # Store the selected item for later reference when saving
            # root.selected_item = selected_item  # Store the selected item in the root window
            setattr(root, "selected_item", selected_item)

    def duplicate_clip():
        selected_item = video_tree.selection()
        if selected_item:
            # Get the values of the selected item
            values = video_tree.item(selected_item, "values")
            exercise_name = values[0]
            video_link = values[1]
            start_time = values[2]
            end_time = values[3]

            # Add a duplicated clip to the Treeview
            video_tree.insert("", "end", values=(exercise_name, video_link, start_time, end_time))

            # Add a duplicated clip to the JSON data
            exercise_clip_data[exercise_name].append({
                "link": video_link,
                "start_timestamp": start_time,
                "end_timestamp": end_time
            })

            save_json_data(exercise_clips_file_path)

    def save_edited_clip():
        selected_item = getattr(root, "selected_item", None)  # Retrieve the stored selected item
        if selected_item:
            # Get the values from the input fields
            exercise_name = exercise_name_entry.get().strip()
            video_link = video_link_entry.get().strip()
            start_timestamp = start_timestamp_entry.get().strip()
            end_timestamp = end_timestamp_entry.get().strip()

            print("Selected item:", exercise_name, video_link, start_timestamp, end_timestamp)

            # # Update the selected clip in the Treeview
            # video_tree.item(selected_item, values=(exercise_name, video_link, start_timestamp, end_timestamp))

            # Get the previous values of the selected clip 
            old_exercise_name = video_tree.item(selected_item, "values")[0]
            old_link = video_tree.item(selected_item, "values")[1]
            old_start_time = video_tree.item(selected_item, "values")[2]
            old_end_time = video_tree.item(selected_item, "values")[3]

            # Check if any of the values (exercise name, link, start time, end time) have changed
            exercise_name_changed = exercise_name != old_exercise_name
            link_changed = video_link != old_link
            start_time_changed = start_timestamp != old_start_time
            end_time_changed = end_timestamp != old_end_time

             # Check if the exercise name is unique (not already present in the exercise_clip_data)
            is_unique_exercise_name = exercise_name not in exercise_clip_data

            if exercise_name_changed:
                # If the exercise name has changed, update the selected clip's exercise name
                # and keep the clip data under both the old and new exercise names
                video_tree.item(selected_item, values=(exercise_name, video_link, start_timestamp, end_timestamp))
                if exercise_name not in exercise_clip_data:
                    exercise_clip_data[exercise_name] = []
                exercise_clip_data[exercise_name].append({
                    "link": video_link,
                    "start_timestamp": start_timestamp,
                    "end_timestamp": end_timestamp
                })

                for video in exercise_clip_data[exercise_name]:
                    if video["link"] == old_link and video["start_timestamp"] == old_start_time and video["end_timestamp"] == old_end_time:
                        exercise_clip_data[old_exercise_name].remove(video)
                        break
            # If any of the values (link, start time, end time) have changed, update the selected clip's data
            if link_changed or start_time_changed or end_time_changed:
                for video in exercise_clip_data[exercise_name]:
                    if video["link"] == old_link and video["start_timestamp"] == old_start_time and video["end_timestamp"] == old_end_time:
                        video["link"] = video_link
                        video["start_timestamp"] = start_timestamp
                        video["end_timestamp"] = end_timestamp
                        break


            # Hide the "Save" button and show the "Add" button
            save_button.grid_remove()
            add_button.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

            # Clear the input fields
            exercise_name_entry.delete(0, tk.END)
            video_link_entry.delete(0, tk.END)
            start_timestamp_entry.delete(0, tk.END)
            end_timestamp_entry.delete(0, tk.END)

            # Update the video list and save the data to the file
            update_video_list()
            save_json_data(exercise_clips_file_path)

    def valid_timestamp_format(timestamp):
        # Check if the timestamp has the format "MM:SS"
        if not re.match(r"^\d{1,2}:\d{2}$", timestamp):
            return False

        # Additional checks for valid MM and SS values
        minutes, seconds = timestamp.split(":")
        if int(minutes) < 0 or int(minutes) >= 60 or int(seconds) < 0 or int(seconds) >= 60:
            return False

        return True

    def update_video_list():
        # video_list.delete(0, tk.END)

        # for exercise, videos in exercise_clip_data.items():
        #     if videos:
        #         for video in videos:
        #             video_list.insert(tk.END, f"{exercise} - {video['link']}")
        # Clear the existing items in the Treeview
        video_tree.delete(*video_tree.get_children())

        # Update the Treeview with the video links grouped under exercise names
        for exercise, videos in exercise_clip_data.items():
            for video in videos:
                video_tree.insert("", "end", values=(exercise, video["link"], video["start_timestamp"], video["end_timestamp"]))

    def treeview_sort_column(tree, col, reverse):
        # Helper function for sorting columns in the Treeview
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

    
    customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

    root = customtkinter.CTk()  # create CTk window like you do with the Tk window

    # style = ThemedStyle(root)
    # style.set_theme("yaru")  # Choose a modern theme, e.g., "plastik"

    root.title("Exercise Video Manager")
    # Set the column and row configurations to expand and fill available space
    root.columnconfigure(0, weight=1)  # Column 0 will expand horizontally
    root.rowconfigure(1, weight=1)  # Row 7 (the Listbox) will expand vertically



    # Create GUI elements with the updated style

    # Labels
    exercise_name_label = customtkinter.CTkLabel(root, text="Exercise Name:", font = ("Futura", 14))
    exercise_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

    video_link_label = customtkinter.CTkLabel(root, text="Video Link:", font = ("Futura", 14))
    video_link_label.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

    start_timestamp_label = customtkinter.CTkLabel(root, text="Start Timestamp (MM:SS):", font = ("Futura", 14))
    start_timestamp_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    end_timestamp_label = customtkinter.CTkLabel(root, text="End Timestamp (MM:SS):", font = ("Futura", 14))
    end_timestamp_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    status_label = customtkinter.CTkLabel(root, text="", text_color="green", font = ("Futura", 14))
    status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    video_list_label = customtkinter.CTkLabel(root, text="Video List", font = ("Futura", 24))
    video_list_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Entry fields
    exercise_name_entry = customtkinter.CTkEntry(root)
    exercise_name_entry.grid(row=0, column=1, padx=10, pady=10)

    video_link_entry = customtkinter.CTkEntry(root)
    video_link_entry.grid(row=1, column=1, padx=10, pady=10, sticky = "e")

    start_timestamp_entry = customtkinter.CTkEntry(root)
    start_timestamp_entry.grid(row=2, column=1, padx=10, pady=10)

    end_timestamp_entry = customtkinter.CTkEntry(root)
    end_timestamp_entry.grid(row=3, column=1, padx=10, pady=10)

    # Buttons
    add_button = customtkinter.CTkButton(root, text="Add Video", command=add_video, fg_color = "#5adbb5", text_color= "black", font = ("Futura", 14))
    add_button.grid(row=4, column=1, padx=10, pady=10, sticky = "ew")



    # Create the "Save" button (initially hidden)
    save_button = customtkinter.CTkButton(root, text="Save", command=save_edited_clip, fg_color="gray", text_color="black", font=("Futura", 14))
    save_button.grid(row=4, column=2, padx=10, pady=10, sticky="ew")
    save_button.grid_remove()  # Hide the "Save" button initially
        

    # Create a Treeview to display the video list with subheadings
    video_tree = ttk.Treeview(root, columns=("Exercise", "Link", "Start Time", "End Time"), show="headings")
    video_tree.heading("Exercise", text="Exercise")
    video_tree.heading("Link", text="Link")
    video_tree.heading("Start Time", text="Start Time")
    video_tree.heading("End Time", text="End Time")

   

    
    # Insert data into the Treeview
    for exercise, videos in exercise_clip_data.items():
        for video in videos:
            video_tree.insert("", "end", values=(exercise, video["link"], video["start_timestamp"], video["end_timestamp"]))

    video_tree.grid(row=0, column=0, sticky="nsew")

    # Enable resizing the columns of the Treeview
    for col in ("Exercise", "Link", "Start Time", "End Time"):
        video_tree.column(col, anchor="center")
        video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    video_tree.grid(row=7, column=0, sticky="nsew", columnspan=2, padx=10, pady=10)

    # # Enable resizing the columns of the Treeview
    # for col in ("Link", "Start Time", "End Time"):
    #     video_tree.column(col, anchor="center")
    #     video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    
    # Enable resizing the columns of the Treeview
    for col in ("Exercise", "Link", "Start Time", "End Time"):
        video_tree.column(col, anchor="center")
        video_tree.heading(col, command=lambda _col=col: treeview_sort_column(video_tree, _col, False))

    # Create vertical scrollbar for the Treeview
    vsb = ttk.Scrollbar(root, orient="vertical", command=video_tree.yview)
    video_tree.configure(yscrollcommand=vsb.set)
    # video_tree.tag_configure("Treeview.Heading", font=("Futura", 18))
    # video_tree.tag_configure("Treeview.Content", font=("Futura", 18))

    # Create a right-click context menu
    right_click_menu = tk.Menu(root, tearoff=0)
    right_click_menu.add_command(label="Edit", command=edit_clip)
    right_click_menu.add_command(label="Duplicate", command=duplicate_clip)

    # # Create an option menu for right-click actions
    # optionmenu_var = customtkinter.StringVar(value="Edit")  # Initialize with "Edit" option
    # optionmenu = customtkinter.CTkOptionMenu(
    #     root, values=["Edit", "Duplicate"], variable=optionmenu_var, command=optionmenu_callback
    # )

    # Bind the right-click event to show the context menu
    video_tree.bind("<Button-2>", show_context_menu)

    # Place the option menu in the GUI layout
    # optionmenu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    # Create the Delete button
    delete_button = customtkinter.CTkButton(root, text="Delete", command=delete_video,fg_color= "red",  font = ("Futura", 14))
    delete_button.grid(row=9, column=1, padx=10, pady=10, sticky="ew")

    status_label = customtkinter.CTkLabel(root, text="", text_color="red", font = ("Futura", 18))
    status_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10)


    # Start with an initial video list
    update_video_list()

    # Run the main event loop
    root.mainloop()

def time_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(":"))
        total_seconds = minutes * 60 + seconds
        return total_seconds
    except ValueError:
        return None


if __name__ == "__main__":

    # list of PT exercises
    # ['squats', 'calf raises', 'shoulder press', 'shoulder workout', 'pull up', 'floor knee to chest', 'yoga', 'supine bridge', 'bird dog', 'forward t - right leg', 'lateral lunge', 'lower quarter reach combination', 'modified side plank with hip abduction', 'prone with scapular retraction', 'quadruped alternating arm', 'shoulder abduction with dumbbells', 'side plank on elbow', 'standard plank', 'standing hip abduction', 'standing shoulder abduction slides at wall', 'standing shoulder horizontal abduction with resistance', 'standing isometric shoulder flexion with doorway', 'standing heel raise with hip and knee flexion at wall']

    # _______________________________________GUI PART _______________________________________
    
    exercise_clips_file_path = 'exercise_training_clips.json'
    with open(exercise_clips_file_path, "r") as json_file:
        exercise_clip_data = json.load(json_file)
    
    # print("STARTING UP GUI...")
    # clip_manager_gui()
    # _______________________________________GUI PART ENDS_______________________________________

    # UNCOMMENT THE CODE BELOW AND COMMENT OUT clip_manager_gui() TO PROCESS JSON
    out_folder = 'videos_info/'
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    video_folder = out_folder + 'videos_out/'

    clips_folder_path = out_folder + 'clip_frames/'

    if not os.path.exists(clips_folder_path):
        os.makedirs(clips_folder_path)

    print("Downloading Video")

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic

    
    features_file_path = 'archive_time_series/angles_trial.csv' # Need to add rows to this csv
    labels_file_path = 'archive_time_series/labels.csv' # Need to add rows to this csv


    features = pd.read_csv(features_file_path)
    # print(features)
    features.drop(features.columns[features.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    features_list = features.columns.tolist()
    # print(features.columns)
    # print(features_list)
    features_cont = pd.DataFrame(columns=features_list)

    labels = pd.read_csv(labels_file_path)
    labels_list = labels.columns.tolist()
    labels_cont = pd.DataFrame(columns=labels_list)

    last_vid_id = int(features['vid_id'].iloc[-1])
    vid_id = int(last_vid_id + 1)
    num = int(vid_id)
    BG_COLOR = (192, 192, 192)  # gray

    for exercise, sets in exercise_clip_data.items():
        print(f"Exercise: {exercise}")
        if len(sets) > 0:
            for i, set_info in enumerate(sets, 1):
                video_url = set_info["link"]
                start_time = time_to_seconds(set_info["start_timestamp"])
                end_time = time_to_seconds(set_info["end_timestamp"])
                video_filename = download_youtube_video(video_url, video_folder, num)
                output_folder = clips_folder_path + video_filename + '/'
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                print("Extracting clip")
                extract_clip(video_filename, start_time, end_time, video_folder, output_folder, num)
                new_labels = [num, exercise]
                labels_cont.loc[len(labels_cont)] = new_labels
                print("Added to Labels")
                print(output_folder)
                output_files_list = os.listdir(output_folder)
                frame_order = int(0)
                for file in output_files_list:
                    folder = output_folder + str(file)
                    process_frames(folder, num, frame_order)
                    print(frame_order)
                    frame_order += 1
                num += 1
        else:
            print("No sets for this exercise:.")
        print("\n")

    features_cont['vid_id'] = features_cont['vid_id'].astype(int)
    features_cont['frame_order'] = features_cont['frame_order'].astype(int)


    print(labels_cont)

    labels_cont.reset_index(drop=True, inplace=True)


    if not os.path.exists(labels_file_path):
        labels_cont.to_csv(labels_file_path, index=False)  # Set index=False to avoid writing row numbers
    else:
        # Read the existing data from the CSV file
        existing_data = pd.read_csv(labels_file_path)

        # Append the DataFrame to the existing data
        merged_data = pd.concat([existing_data, labels_cont], ignore_index=True)

        # Write the merged data to the CSV file
        merged_data.to_csv(labels_file_path, index=False)


    if not os.path.exists(features_file_path):
        features_cont.to_csv(features_file_path, index=False)  # Set index=False to avoid writing row numbers

    # If the file already exists, append the data to it
    else:
        # features_cont.to_csv(features_file_path, mode='a', header=False, index=False)
        with open(features_file_path, 'a') as file:
            features_cont.to_csv(file, header=False, index=False)