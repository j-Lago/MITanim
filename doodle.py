



def main():

    coords = (0, 1, 2, 3, 4, 5, 6, 7)
    print(coords)

    for i in range(0, len(coords)-2, 2):
        coords_line = coords[i : i+4]
        print(coords_line)


if __name__ == '__main__':
    main()