# To get history in an interactive Python session
import readline
for i in range(readline.get_current_history_length()):
    print(readline.get_history_item(i + 1))
