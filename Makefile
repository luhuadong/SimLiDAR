CC=gcc
TARGET=SimLiDAR

all:
	$(CC) main.c -o $(TARGET) -g
	$(CC) main.c -o $(TARGET)5 -g -DLASER_MODULE_NUM=5

clean:
	rm $(TARGET) $(TARGET)5
