from logger import logger_instance as log

def ask_user_choice(question, options):
    """
    Ask user a question with options as list or dict.
    If dict, key is returned, value is shown.
    If list, value is returned directly.
    """

    if isinstance(options, dict):
        option_list = list(options.items())  # Convert dict to list of tuples (key, value)
    else:
        option_list = list(enumerate(options, 1))  # Convert list to indexed options

    # Log the question
    log.info(f"\n{question}:")

    # Display options
    for idx, val in option_list:
        log.info(f"{idx}) {val}")

    while True:
        choice = input("Enter your choice: ").strip()

        if isinstance(options, dict):  # Handle dictionary input
            normalized = {str(k).lower(): k for k in options}
            if choice.lower() in normalized:
                return normalized[choice.lower()]
        else:  # Handle list input
            try:
                choice_int = int(choice)
                if 1 <= choice_int <= len(options):
                    return options[choice_int - 1]
            except ValueError:
                pass

        # Invalid choice feedback
        log.warning("Invalid choice. Please try again.")
