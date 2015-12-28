# -*- coding: utf-8 -*-
"""matrix_data

Module containing functions for diecase retrieval and parsing,
diecase storing, parameter searches.
"""
# File operations
import io
import csv
# We need user interface
from rpi2caster.global_settings import USER_INTERFACE as ui
# Some functions raise custom exceptions
from rpi2caster import exceptions
# We need to operate on a database
from rpi2caster import database
# Wedge operations for several matrix-case management functions
from rpi2caster import wedge_data
# Create an instance of Database class with default parameters
DB = database.Database()


def lookup_diecase(type_series, type_size):
    """lookup_diecase

    Searches for a diecase of given type series (e.g. 327) and size (e.g. 12),
    if several matches found - allows to choose one of them, returns data.
    """
    matches = DB.diecase_by_series_and_size(type_series, type_size)
    if len(matches) == 1:
        # One result found
        return matches[0]
    else:
        # More than one match - decide which one to use:
        idents = [record[0] for record in matches]
        # Associate diecases with IDs to select one later
        assoc = dict(zip(idents, matches))
        # Display a menu with diecases from 1 to the last:
        options = [(i, k) for i, k in enumerate(matches, start=1)]
        header = 'Choose a diecase:'
        choice = ui.menu(options, header)
        # Choose one
        chosen_id = options[choice]
        # Return a list with chosen diecase's parameters:
        return assoc[chosen_id]


def list_diecases():
    """Lists all matrix cases we have."""
    data = DB.get_all_diecases()
    results = {}
    ui.display('\n' +
               'Index'.ljust(7) +
               'Diecase ID'.ljust(20) +
               'Type series'.ljust(15) +
               'Type size'.ljust(15) +
               'Wedge series'.ljust(15) +
               'Set width'.ljust(15) +
               'Typeface name' + '\n')
    for index, diecase in enumerate(data, start=1):
        # Collect diecase parameters
        index = str(index)
        row = [index.ljust(7)]
        row.append(str(diecase[0]).ljust(20))
        row.extend([str(field).ljust(15) for field in diecase[1:-2]])
        # Add number and ID to the result that will be returned
        results[index] = diecase[0]
        # Add typeface name - no justification!
        row.append(diecase[-2])
        ui.display(''.join(row))
    ui.display('\n\n')
    # Now we can return the number - diecase ID pairs
    return results


def choose_diecase():
    """choose_diecase:

    Lists diecases and lets the user choose one; returns the diecase name.
    """
    # Do it only if we have diecases (depends on list_diecases retval)
    while True:
        ui.clear()
        ui.display('Choose a matrix case:', end='\n\n')
        available_diecases = list_diecases()
        # Enter the diecase name
        prompt = 'Number of a diecase? (leave blank to exit): '
        choice = (ui.enter_data_or_blank(prompt) or
                  exceptions.return_to_menu())
        # Safeguards against entering a wrong number or non-numeric string
        try:
            diecase_id = available_diecases[choice]
            return diecase_id
        except KeyError:
            ui.confirm('Diecase number is incorrect! [Enter] to continue...')
            continue


def show_diecase():
    """show_diecase:

    Wrapper function for menu: used for choosing and showing a diecase layout.
    """
    while True:
        # Choose diecase
        diecase_id = choose_diecase()
        # First, get diecase data
        (diecase_id, _, _, wedge_series, set_width,
         _, layout) = DB.diecase_by_id(diecase_id)
        # Process metadata
        # Get wedge unit arrangement
        unit_arr = wedge_data.get_unit_arrangement(wedge_series, set_width)
        ui.display_diecase_layout(layout, unit_arr)
        ui.confirm('[Enter] to continue...')


def add_diecase():
    """add_diecase:

    Adds a matrix case to the database.
    Can be called with arguments from another function, or the user can enter
    the data manually.
    Displays info and asks for confirmation.
    """
    prompt = 'Diecase ID? (leave blank to exit) : '
    diecase_id = ui.enter_data_or_blank(prompt) or exceptions.return_to_menu()
    type_series = ui.enter_data('Fount series: ')
    type_size = ui.enter_data('Type size (end with D for Didot): ')
    wedge_series = ui.enter_data('Wedge/stopbar series for this typeface: ')
    # If we enter S5 etc. - save it as 5
    wedge_series = wedge_series.strip('sS')
    set_width = ui.enter_data_spec_type('Set width (decimal): ', float)
    typeface_name = ui.enter_data('Typeface name: ')
    # Start with an empty layout
    layout = None
    # Ask if we want to enter a layout file
    if ui.yes_or_no('Add layout from file?'):
        layout = submit_layout_file()
    # Edit the layout
    if ui.yes_or_no('Edit the layout file?'):
        layout = ui.edit_diecase_layout(layout)
    # Display parameters before asking to commit
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
    for line in info:
        ui.display(line)
    # Ask for confirmation
    if ui.yes_or_no('Commit to the database?'):
        DB.add_diecase(diecase_id, type_series, type_size, wedge_series,
                       float(set_width), typeface_name, layout)
        ui.display('Data added successfully.')


def edit_diecase():
    """edit_diecase:

    Chooses and edits a diecase layout.

    If layout is blank, user needs to enter the column and row numbers.
    Displays characters that were previously in position,
    allows to change them.
    A matrix can be used or not (for example, multiple-cell mats
    should be addressed only at one of these cells, where the centering pin
    can descend - and not where no hole is made, because trying to
    address such a cell can damage the caster!).
    If user wants to enter a space - decide if it is low or high.
    At the end, confirm and commit."""
    while True:
        diecase_id = choose_diecase()
        layout = get_layout(diecase_id)
        # If layout is empty, user can submit it from file
        if not layout and ui.yes_or_no("Add layout from file?"):
            layout = submit_layout_file()
        # Edit the layout?
        layout = ui.edit_diecase_layout(layout)
        # Ask for confirmation
        ans = ui.yes_or_no('Commit to the database?')
        if ans and DB.update_diecase_layout(diecase_id, layout):
            ui.display('Matrix case layout updated successfully.')


def upload_layout():
    """upload_layout:

    Allows user to upload a matrix case layout from a CSV file.
    At the end, confirm and commit."""
    while True:
        diecase_id = choose_diecase()
        # Load the layout from file? Ask only if no layout at input
        layout = submit_layout_file()
        # Ask for confirmation
        ans = ui.yes_or_no('Commit to the database?')
        if ans and DB.update_diecase_layout(diecase_id, layout):
            ui.display('Matrix case layout uploaded successfully.')


def clear_diecase():
    """clear_diecase:

    Clears the diecase layout, so it can be entered from scratch.
    You usually want to use this if you seriously mess something up.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.update_diecase_layout(diecase_id):
            ui.display('Matrix case purged successfully - now empty.')


def delete_diecase():
    """Used for deleting a diecase from database.

    Lists diecases, then allows user to choose ID.
    """
    while True:
        diecase_id = choose_diecase()
        ans = ui.yes_or_no('Are you sure?')
        if ans and DB.delete_diecase(diecase_id):
            ui.display('Matrix case deleted successfully.')


def get_diecase_parameters(diecase_id):
    """get_diecase_parameters:

    Displays parameters for a chosen matrix case and returns them.
    """
    (diecase_id, type_series, type_size, wedge_series, set_width,
     typeface_name, layout) = DB.diecase_by_id(diecase_id)
    # Display parameters before editing
    info = []
    info.append('Diecase ID: %s' % diecase_id)
    info.append('Type series: %s' % type_series)
    info.append('Type size: %s' % type_size)
    info.append('Wedge series: %s' % wedge_series)
    info.append('Set width: %s' % set_width)
    info.append('Typeface name: %s' % typeface_name)
    info.append('Styles present: %s' % ', '.join(get_styles(layout)))
    for line in info:
        ui.display(line)
    ui.display('\n\n')
    # Return data for further processing
    return (type_series, type_size, wedge_series, set_width,
            typeface_name, layout)


def get_layout(diecase_id):
    """get_layout:

    Displays parameters for a chosen matrix case and returns them.
    """
    layout = DB.diecase_by_id(diecase_id)[-1]
    return layout


def get_styles(layout):
    """Parses the diecase layout and gets available typeface styles.
    Returns a list of them."""
    try:
        return list({style for mat in layout for style in mat[1] if style})
    except TypeError:
        return []


def submit_layout_file():
    """submit_layout_file:

    Reads a matrix case arrangement from a text or csv file.
    The format should be:
    "character";"style1,style2...";"column";"row";"unit_width"
    """
    filename = ui.enter_input_filename()
    if not filename:
        return False
    # Initialize the layout list
    layout = []
    all_records = []
    # This will store the processed combinations - and whenever a duplicate
    # is detected, the function will raise an exception
    combinations = []
    with io.open(filename, 'r') as layout_file:
        input_data = csv.reader(layout_file, delimiter=';', quotechar='"')
        all_records = [record for record in input_data]
        displayed_lines = [' '.join(record) for record in all_records[:5]]
        # Preview file
        ui.display('File preview: displaying first 5 rows:\n')
        ui.display('\n'.join(displayed_lines), end='\n\n')
        # Ask if the first row is a header
        if ui.yes_or_no('Is the 1st row a table header? '):
            all_records.pop(0)
    # Process the records
    for record in all_records:
        # A record is a list with all diecase data:
        # [character, (style1, style2...), column, row, units]
        # Add a character - first item; if it's a space, don't change it
        if record[0] == ' ':
            processed_record = [record[0]]
        else:
            processed_record = [record[0].strip()]
        # Parse the other items and strip the whitespace
        for item in record[1:]:
            item = str(item).strip()
            processed_record.append(item)
        # Get a string containing styles with no whitespace
        styles = processed_record[1].split(',')
        processed_styles = ','.join([style.strip() for style in styles])
        processed_record[1] = processed_styles
        # For code clarity
        row = processed_record[2]
        column = processed_record[3]
        # Print the duplicates
        if (row, column) in combinations:
            prompt = ('You already have a matrix at this position: %s %s'
                      % (row, column))
            ui.display(prompt)
        # Add a list to the layout
        layout.append(processed_record)
        # Add coordinates to the list
        if row and column:
            combinations.append((row, column))
    # We now have completed uploading a layout and making a list out of it
    return layout
