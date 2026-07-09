def user_profile_set_property(username: str, property: str, value: str):
    """
    Sets a property value for a specific user profile.

    Args:
        username: The unique, human-readable identifier for the user.
        property: The name of the property to set (must be unique per user).
        value: The value to assign to the property as a string.
    """


def user_profile_update_property(username: str, property: str, value: str):
    """
    Updates an existing property for a specific user profile. If the property does not exist for the given user, no changes are made.

    Args:
        username: The unique, human-readable identifier for the user.
        property: The name of the existing property to update.
        value: The new value to assign to the property.
    """


def user_profile_rename_property(username: str, old_property: str, new_property: str):
    """
    Renames an existing property to a new name for a specific user profile.

    Args:
        username: The unique, human-readable identifier for the user.
        old_property: The current name of the property to be renamed.
        new_property: The new name to assign to the property.
    """


def user_profile_remove_property(username: str, property: str):
    """
    Removes a specific property from a user profile.

    Args:
        username: The unique, human-readable identifier for the user.
        property: The name of the property to be deleted.
    """


def user_profile_get_property(username: str, property: str):
    """
    Retrieves a property value from a specific user profile.

    Args:
        username: The unique, human-readable identifier for the user.
        property: The name of the property to retrieve.
    """


def user_profile_list_properties(username: str):
    """
    Lists all properties and their values for a specific user profile.

    Args:
        username: The unique, human-readable identifier for the user.
    """
