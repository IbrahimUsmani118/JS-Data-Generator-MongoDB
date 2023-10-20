# add_data.py

def get_user_data():
    data_list = []

    while True:
        user_input = input("Enter data (or 'done' to stop): ")
        if user_input.lower() == 'done':
            break
        data_list.append(user_input)

    return data_list

if __name__ == "__main__":
    data = get_user_data()
    print("Data input complete.")
