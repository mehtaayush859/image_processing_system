# image_processing_system
This is an simple backend system where user provides the image as input in (jpg, jpeg, png) format and perform specific operations and get the specific output as expected.

#Steps to Run Program

1. Run the server.py file on CLI. # python server.py
2. Run the client.py file in other CLI terminal. # python client.py
3. After running client file, it will as for input as, provide file_path (try content root, absolute path if any doesnt't work). Make sure path is coorect and provide the path of image.
4. It will load original image first and defalt viewer for windows, and then will ask to perform operation like rotate, resize etc.
5. Provide the inputs coorectly, other wise it will how invalid and ask again.
6. After completing user operations, finally provide "done" string as stated in terminal.
7. The code will complete its execution and will show the updated image with all processed operations.
8. If thumbnail is present it will also pop up and user should have a look at it.
9. You can verify the operations performed on terminal in client side.
10. If, necessary the server also maintains and displays the logs/action performed on image in its terminal.
11. After execution close the server file.
12. If want, to re run again, follow the steps again.
