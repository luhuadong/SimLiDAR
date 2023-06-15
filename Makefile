CC?=gcc
TARGET=SimLiDAR
FLAGS_RAW=-DUSING_RAW_SOCKET
FLAGS_A0X=-DLASER_MODULE_NUM=5

all:
	$(CC) main.c mysocket.c -o $(TARGET) -g $(FLAGS_RAW)
	$(CC) main.c mysocket.c -o $(TARGET)5 -g $(FLAGS_A0X) 

clean:
	rm $(TARGET) $(TARGET)5
