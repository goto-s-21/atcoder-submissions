X, Y = input().split()

if X == "Lynx" and (Y == "Lynx" or Y == "Serval" or Y == "Ocelot"):
    print("Yes")

elif X == "Serval" and Y == "Lynx":
    print("No")

elif X == "Serval" and (Y == "Serval" or Y == "Ocelot"):
    print("Yes")

elif X == "Ocelot" and Y == "Ocelot":
    print("Yes")

elif X == "Ocelot" and (Y == "Serval" or Y == "Lynx"):
    print("No")