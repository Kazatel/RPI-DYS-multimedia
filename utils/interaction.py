def ask_user_choice(question, options, log=None):
    """
    Ask user a question with options as list or dict.
    If dict, key is returned, value is shown.
    If list, value is returned directly.
    """
    if isinstance(options, dict):
        option_list = list(options.items())
    else:
        option_list = list(enumerate(options, 1))

    if log:
        log.p_info(f"\n{question}:")
    else:
        print(f"\n{question}:")

    for idx, val in option_list:
        print(f"{idx}) {val}")

    while True:
        choice = input("Enter your choice: ").strip()

        if isinstance(options, dict):
            normalized = {str(k).lower(): k for k in options}
            if choice.lower() in normalized:
                return normalized[choice.lower()]
        else:
            try:
                choice_int = int(choice)
                if 1 <= choice_int <= len(options):
                    return options[choice_int - 1]
            except ValueError:
                pass

        if log:
            log.p_warning("Invalid choice. Try again.")
        else:
            print("Invalid choice. Try again.")
