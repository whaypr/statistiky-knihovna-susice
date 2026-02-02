# Sušice Municipal Library Open Data Visualization

This application provides a dynamic and interactive visualization of the [open data published by the Sušice Municipal Library](https://susice.tritius.cz/statistics).

The data used for visualization are automatically parsed from the library’s website using the `app/data_parsing.py` script and stored as CSV files. These files are then loaded and processed by the application.

The application is available **online** at:  
👉 https://sks.pdddd.one/

---

## Developer Guide

All components of the application are executed from the **project root directory**.

### Data Fetching

To fetch and parse the data, run:
```
$ python app/data_parsing.py
```

**Notes:**
- The script creates the required directory structure and populates it with data in CSV format.
- Although the script can be executed from any directory, the data required by the application must be generated in the **project root directory**.
- Running the script is not strictly necessary, as the data are already included in the repository.
- The script can be used to fetch the latest data; it always re-parses **all** available data, not just new entries.
- Existing data do not need to be deleted before running the script.
- The same script is used by the application itself to automatically download updated data every hour.

---

### Running the Application

To start the application, run:
```
$ python app/data_visualization.py
```

This command launches a Flask server hosting the application.

The application will be available locally at:  
👉 http://127.0.0.1:8050/

---

### Running Tests

To execute the parsing tests, run:
```
$ pytest tests/test_parsing.py
```
