def ask_user_choice(question, options):
    """
    Ask user a question with options as list or dict.
    If dict, key is returned, value is shown.
    """
    if isinstance(options, dict):
        option_list = list(options.items())
    else:
        option_list = list(enumerate(options, 1))

    print(f"\n{question}:")
    for idx, val in option_list:
        print(f"{idx}) {val}")

    while True:
        choice = input("Enter your choice: ").strip()
        if isinstance(options, dict):
            if choice in options:
                return choice
        else:
            try:
                choice_int = int(choice)
                if 1 <= choice_int <= len(options):
                    return options[choice_int - 1]
            except ValueError:
                pass
        print("Invalid choice. Try again.")

