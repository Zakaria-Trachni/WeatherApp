import requests
from customtkinter import *
from PIL import Image
from tkinter import PhotoImage, messagebox, Canvas
from collections import defaultdict
from datetime import datetime, timedelta, timezone

class Time:
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    root.geometry(f"{width}x{height}+{x}+{y}")

def get_current_weather(city):
    API_key = "cfa6c9588da11f33468eb2f757096153"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    result =  requests.get(url)

    # if the city not found:
    if result.status_code == 404:
        messagebox.showwarning("Error", "City not found!")
        return None
    
    # if the city exist:
    weather = result.json()

    city = weather['name']
    country = weather['sys']['country']
    timezone_offset = weather['timezone']
    location_time = get_time(timezone_offset)
    sunrise_timestamp = weather['sys']['sunrise']
    sunset_timestamp = weather['sys']['sunset']
    sunrise, sunset = sunrise_sunset(sunrise_timestamp, sunset_timestamp, timezone_offset)
    lon = weather['coord']['lon'] # Longitude
    lat = weather['coord']['lat'] # Latitude
    city_icon_id = weather['weather'][0]['icon']
    # icon_url = f"https://openweathermap.org/img/wn/{city_icon_id}@2x.png"
    temperature = weather['main']['temp'] - 273.15
    max_temp = weather['main']['temp_max'] - 273.15
    min_temp = weather['main']['temp_min'] - 273.15
    description = weather['weather'][0]['description']
    humidity = weather["main"]["humidity"]
    pressure = weather["main"]["pressure"]
    wind_speed = weather["wind"]["speed"]

    return (city, country, location_time, sunrise, sunset, lon, lat, city_icon_id, temperature, max_temp, min_temp, description, humidity, pressure, wind_speed)

def get_time(timezone_offset):
    utc_now = datetime.now(timezone.utc)
    # Convert the timezone offset from seconds to hours
    timezone_offset_hours = timezone_offset / 3600
    # Add the timezone offset to the UTC time to get the local time
    local_time = utc_now + timedelta(hours=timezone_offset_hours)
    
    return Time(local_time.hour, local_time.minute)

def sunrise_sunset(sunrise_timestamp, sunset_timestamp, timezone_offset):
    timezone_offset_hours = timezone_offset / 3600

    sunrise_datetime = datetime.fromtimestamp(sunrise_timestamp) + timedelta(hours=(timezone_offset_hours-1))
    sunset_datetime = datetime.fromtimestamp(sunset_timestamp) + timedelta(hours=(timezone_offset_hours-1))

    return (Time(sunrise_datetime.hour, sunrise_datetime.minute), Time(sunset_datetime.hour, sunset_datetime.minute))

def main():
    root = CTk()
    root.title("Weather App")
    center_window(root, 800, 620)
    root.resizable(False, False)
    set_appearance_mode("dark")
    set_default_color_theme("green")
    icon = PhotoImage(file='images/icon.png')
    root.iconphoto(True, icon)

    # // functions:

    def update_screen(city):
        city_weather = get_current_weather(city)

        # if the city not found:
        if city_weather is None:
            return
        
        # if the city exist:
        city, country, location_time, sunrise, sunset, lon, lat, city_icon_id, temperature, max_temp, min_temp, description, humidity, pressure, wind_speed = city_weather

        time_label.configure(text=f"{location_time.hour:02d}:{location_time.minute:02d}")
        location_label.configure(text=f"{city} / {country}")
        sunrise_label.configure(text=f"Sunrise: {sunrise.hour:02d}:{sunrise.minute:02d}")
        sunset_label.configure(text=f"Sunset: {sunset.hour:02d}:{sunset.minute:02d}")
        E_N_label.configure(text=f"{lat}°N,  {lon}°E")
        # image = Image.open(requests.get(icon_url, stream=True).raw)
        image = Image.open(f"weather icons/{city_icon_id}@2x.png")
        weather_image = CTkImage(light_image=image, dark_image=image, size=(150,150))
        weather_icon.configure(image=weather_image)
        temperature_label.configure(text=f"{round(temperature)}°C")
        max_min_label.configure(text=f"{round(max_temp)}°C / {round(min_temp)}°C")
        description_label.configure(text=f"{description.title()}")
        humidity_value.configure(text=f"{humidity}%")
        pressure_value.configure(text=f"{pressure} hPA")
        wind_value.configure(text=f"{wind_speed} m/s")

    def forecast_5days_data(city):
        API_key = "cfa6c9588da11f33468eb2f757096153"
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_key}&units=metric&cnt=40"
        
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code}")
            return None

    def update_canvas(city):
        ## updating the weather 5 days forecast labels:
        if forecast_5days_data(city):
            data = forecast_5days_data(city)
            # Add frames, each containing three labels arranged in a grid:
            for i, forecast in enumerate(data['list']):
                # if i>8: # To minimize the lunching time - Remove this line if you want the whole 5days forecast.
                #     break

                dt_txt = forecast['dt_txt']
                dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                time_str = dt.strftime("%H:%M")
                day = dt.strftime("%d")
                mon = dt.strftime("%m")

                temp = forecast['main']['temp']
                icon_code = forecast['weather'][0]['icon']
                # icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

                # Add labels inside each frame
                for j in range(3):
                    if j==0:
                        labels[i*3+j].configure(text=f"{day}/{mon}\n{time_str}")
                    elif j==1:
                        # image = Image.open(requests.get(icon_url, stream=True).raw)
                        image = Image.open(f"weather icons/{icon_code}@2x.png")
                        weather_image = CTkImage(light_image=image, dark_image=image, size=(80,80))
                        labels[i*3+j].configure(image=weather_image)
                    else:
                        labels[i*3+j].configure(text=f"{round(temp)}°C")

    def canvas_settings():
        global labels
        ## // --> Scrollable frame design:
        def on_horizontal(event):
            # Scroll horizontally based on mouse wheel movement
            canvas.xview_scroll(-1 * event.delta, 'units')

        def configure_canvas(event=None):
            # Update the canvas scroll region to the size of the scrollable frame
            canvas.config(scrollregion=canvas.bbox("all"))

        scrollable_frame = CTkFrame(canvas, width=3000, height=100, fg_color="transparent")
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Bind horizontal scrolling to shift+mousewheel
        root.bind_all('<Shift-MouseWheel>', on_horizontal)

        # Update the scroll region of the canvas
        scrollable_frame.bind("<Configure>", configure_canvas)
        configure_canvas()  # Initial call to set the scroll region

        ## // --> Getting weather informations:
        if forecast_5days_data("New York"):
            data = forecast_5days_data("New York")

            labels =[]
            frames = []
            # Add 20 frames, each containing three labels arranged in a grid
            for i, forecast in enumerate(data['list']):
                # if i>8:   # To minimize the lunching time - Remove this line if you want the whole 5days forecast.
                #     break

                dt_txt = forecast['dt_txt']
                dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                time_str = dt.strftime("%H:%M")
                day = dt.strftime("%d")
                mon = dt.strftime("%m")
        
                temp = forecast['main']['temp']
                icon_code = forecast['weather'][0]['icon']
                # icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

                # Create frames
                frame = CTkFrame(scrollable_frame, border_width=3, border_color='#354230', width=200)
                frame.grid(row=0, column=i, padx=15, pady=10)
                frames.append(frame)

                # Add labels inside each frame
                for j in range(3):
                    if j==0:
                        label = CTkLabel(frame, text=f"{day}/{mon}\n{time_str}", padx=10)
                    elif j==1:
                        # image = Image.open(requests.get(icon_url, stream=True).raw)
                        image = Image.open(f"weather icons/{icon_code}@2x.png")
                        weather_image = CTkImage(light_image=image, dark_image=image, size=(80,80))
                        label = CTkLabel(frame, text="", image=weather_image, height=50, wraplength=50)
                    else:
                        label = CTkLabel(frame, text=f"{round(temp)}°C", padx=10)
                    label.grid(row=j, column=0, padx=5, pady=5)
                    labels.append(label)

    def update_fourth_frame(city):
        if forecast_5days_data(city):
            data = forecast_5days_data(city)

            daily_data = defaultdict(lambda: {'temps': [], 'icons': []})

            # Iterate over the forecast data
            for forecast in data['list']:
                dt_txt = forecast['dt_txt']
                dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                day_of_week = dt.strftime("%A")  # Get the full weekday name (e.g., Monday, Tuesday)
                
                temp = forecast['main']['temp']
                icon_code = forecast['weather'][0]['icon']
                
                # Store temperatures and icons by day of the week
                daily_data[day_of_week]['temps'].append(temp)
                daily_data[day_of_week]['icons'].append(icon_code)
            
            i=0
            for day, info in daily_data.items():
                max_temp = round(max(info['temps']))
                min_temp = round(min(info['temps']))
                icon = info['icons'][0]  # Just taking the first icon for simplicity
                # icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"

                for j in range(3):
                    if j==0:
                        days_labels[i].configure(text=f"{day}")
                    elif j==1:
                        # image = Image.open(requests.get(icon_url, stream=True).raw)
                        image = Image.open(f"weather icons/{icon}@2x.png")
                        weather_image = CTkImage(light_image=image, dark_image=image, size=(60,60))
                        days_labels[i+1].configure(image=weather_image)
                    else:
                        days_labels[i+2].configure(text=f"{max_temp}/{min_temp} °C")
                i+=3

    def search(event=None): # Add "event=None" because the function doesn’t need to use the event object
        city = city_etry.get()
        if city:
            update_screen(city)
            update_canvas(city)
            update_fourth_frame(city)

    # // frames:
    principal_frame = CTkFrame(root)
    principal_frame.pack(expand=True, fill="both")

    first_frame = CTkFrame(principal_frame, height=120, fg_color='#253949', border_width=5, border_color="#354230")
    first_frame.pack_propagate(False)
    first_frame.pack(fill='x', padx=10, pady=(10,5))
    # sub-frames on the first frame:
    ff_one = CTkFrame(first_frame, fg_color='#253949')
    ff_one.pack_propagate(False)
    ff_one.pack(expand=True, fill='both', side="left", padx=5, pady=5)
    ff_two = CTkFrame(first_frame, width=200, fg_color='#253949')
    ff_two.pack_propagate(False)
    ff_two.pack(fill='y', side="left", padx=5, pady=5)

    main_frame = CTkFrame(principal_frame, height=300, fg_color='transparent')
    main_frame.pack(expand=True, fill='both', padx=10, pady=5)
    # sub-frames on the main frame:
    second_frame = CTkFrame(main_frame, width=250, fg_color='#253949', border_width=5, border_color="#354230")
    second_frame.pack_propagate(False)
    second_frame.pack(fill='y', side="left")
    third_frame_one = CTkFrame(main_frame, fg_color='#253949', border_width=5, border_color="#354230")
    third_frame_one.pack_propagate(False)
    third_frame_one.pack(fill='x', padx=(5,0), pady=(0,5))
    third_frame_two = CTkFrame(main_frame, height=200, fg_color="#253949", border_width=5, border_color='#354230')
    third_frame_two.pack_propagate(False)
    third_frame_two.pack(expand=True, fill='both', padx=(5,0))

    fourth_frame = CTkFrame(principal_frame, height=170, fg_color='#253949', border_width=5, border_color="#354230")
    fourth_frame.pack_propagate(False)
    fourth_frame.pack(fill='x', padx=10, pady=(5,10))

    # // frames rows/columns configuration:
    for i in range(4):
        ff_two.grid_rowconfigure(i, weight=1)
    
    for i in range(6):
        third_frame_one.grid_rowconfigure(i, weight=1)
    for i in range(4):
        third_frame_one.grid_columnconfigure(i, weight=1)


    # // labels, buttons,.. :
    # -> first frame:
    time_label = CTkLabel(ff_one, text="00:00", font=("Helvetica", 30, "bold"), anchor='center')
    image = Image.open('images/weather.png')
    weather_label_icon = CTkImage(light_image=image, dark_image=image, size=(90,90))
    icon_label = CTkLabel(ff_one, text="", image=weather_label_icon)
    city_etry = CTkEntry(ff_one, font=("Helvitica", 18))
    image = Image.open('images/search.png')
    search_icon = CTkImage(light_image=image, dark_image=image, size=(27,27))
    search_btn = CTkButton(ff_one, text="", image=search_icon, width=40, fg_color="transparent", hover_color="#354230", command=search)
    location_label = CTkLabel(ff_two, text="City / Country", font=("Helvitica", 16, "bold"), anchor='e')
    sunrise_label = CTkLabel(ff_two, text="Sunrise: 00:00", font=("Helvitica", 14), anchor='e')
    sunset_label = CTkLabel(ff_two, text="Sunset: 00:00", font=("Helvitica", 14), width=170, anchor='e')
    E_N_label = CTkLabel(ff_two, text="__ °N,  __ °E", font=("Helvitica", 14), anchor='e')

    time_label.pack(side='left', padx=(30,120), pady=10)
    icon_label.pack(side='left', padx=5, pady=10)
    city_etry.pack(side='left', padx=5, pady=10, anchor='center')
    search_btn.pack(side='left', pady=10, anchor='center')
    location_label.grid(row=0, column=0, padx=10, pady=(3,0), sticky='e')
    sunrise_label.grid(row=1, column=0, padx=10, sticky='e')
    sunset_label.grid(row=2, column=0, padx=10, sticky='e')
    E_N_label.grid(row=3, column=0, padx=10, pady=(0,3), sticky='e')

    # -> second frame:
    weather_icon = CTkLabel(second_frame, text="")
    temperature_label = CTkLabel(second_frame, text="27°C", font=("Helvetica", 26))
    max_min_label = CTkLabel(second_frame, text="31°C / 22°C")
    description_label = CTkLabel(second_frame, text="Moderate rain")


    weather_icon.pack(pady=5)
    temperature_label.pack()
    max_min_label.pack()
    description_label.pack()

    # -> third frame:
    humidity = CTkLabel(third_frame_one, text="Humidity", font=("Helvetica", 18))
    humidity_value = CTkLabel(third_frame_one, text="00%", font=("Helvetica", 18))
    pressure_label = CTkLabel(third_frame_one, text="Pressure", font=("Helvetica", 18))
    pressure_value = CTkLabel(third_frame_one, text="000 hPa", font=("Helvetica", 18))
    wind_label = CTkLabel(third_frame_one, text="Wind speed", font=("Helvetica", 18))
    wind_value = CTkLabel(third_frame_one, text="0,00 m/s", font=("Helvetica", 18))
    
    humidity.grid(row=2, column=1, pady=(10,0), sticky='nwse')
    humidity_value.grid(row=2, column=2, pady=(10,0), sticky='w')
    pressure_label.grid(row=3, column=1, sticky='nwse')
    pressure_value.grid(row=3, column=2, sticky='w')
    wind_label.grid(row=4, column=1, pady=(0,10), sticky='nwse')
    wind_value.grid(row=4, column=2, pady=(0,10), sticky='w')

    canvas = Canvas(third_frame_two, bg="#253949", highlightthickness=0)
    canvas.pack(fill='both', expand=True, padx=5, pady=5)
    canvas_settings()

    # -> fourth frame:
    global days_labels
    days_frames = []
    days_labels = []
    for i in range(6):
        # create frames:
        if i==0:
            frame = CTkFrame(fourth_frame, border_width=3, border_color='#354230', width=150)
            frame.pack_propagate(False)
            frame.pack(side="left", padx=(15,10), pady=10)
        else:
            frame = CTkFrame(fourth_frame, border_width=3, border_color='#354230', width=100)
            frame.pack_propagate(False)
            frame.pack(side="left", padx=10, pady=10)
        days_frames.append(frame)

        # put labels inside each frame:
        for j in range(3):
            if j==0:
                label = CTkLabel(frame, text="",font=("Helvitica", 14))
                label.pack(pady=(5,0))
            elif j==1:
                label = CTkLabel(frame, text="")
                label.pack(pady=1)
            else:
                label = CTkLabel(frame, text="",font=("Helvitica", 14))
                label.pack(pady=(0,5))
            days_labels.append(label)

    days_labels[0].configure(font=("Helvitica", 16, "bold"))


    # // bind
    city_etry.bind('<Return>', search)


    # run
    update_screen("New York")
    update_fourth_frame("New York")
    root.mainloop()

if __name__ == "__main__":
    main()