with open("geminiapi.env") as api:
    print(api.readlines()[1].split("=")[1])
    