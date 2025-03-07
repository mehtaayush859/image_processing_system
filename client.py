import grpc
import image_processor_pb2
import image_processor_pb2_grpc
import os


class GrpcImageClient:
    def __init__(self, server_address="localhost:50051"):
        """Initialize the gRPC client."""
        self.channel = grpc.insecure_channel(server_address)
        self.stub = image_processor_pb2_grpc.ImageProcessorStub(self.channel)
        self.current_image_data = None
        self.operations = []
        self.rotate_degrees = 0
        self.resize_width = 0
        self.resize_height = 0
        self.generate_thumbnail = False
        self.thumb_width = 30
        self.thumb_height = 30

    def load_image(self, image_path):
        """Load image from the provided file path with error handling."""
        while True:
            try:
                with open(image_path, "rb") as f:
                    self.current_image_data = f.read()
                print("Loaded Original Image.")
                self.display_image(self.current_image_data, "original_image.png")
                break
            except FileNotFoundError:
                print("Error: File not found. Please enter a valid image path.")
                image_path = input("Enter the image file path: ").strip()
            except Exception as e:
                print(f"Error: {e}. Please enter a valid image path.")
                image_path = input("Enter the image file path: ").strip()

    def display_image(self, image_data, filename="temp_image.png"):
        """Save the image temporarily and open it in the default system viewer."""
        with open(filename, "wb") as f:
            f.write(image_data)

        os.startfile(filename)

    def process_image(self):
        """Send a single API call to process the image with all selected operations."""
        print("\n Operations to be applied:")
        if self.operations:
            for op in self.operations:
                print(f"   - {op.replace('_', ' ').capitalize()}")
        if self.rotate_degrees:
            print(f"   - Rotate {self.rotate_degrees}°")
        if self.resize_width and self.resize_height:
            print(f"   - Resize to {self.resize_width}x{self.resize_height}")
        if self.generate_thumbnail:
            print(f"   - Generate Thumbnail ({self.thumb_width}x{self.thumb_height})")
        print("Processing the image... \n")

        request = image_processor_pb2.ImageRequest(
            image_data=self.current_image_data,
            operations=self.operations,
            rotate_degrees=self.rotate_degrees,
            resize_width=self.resize_width,
            resize_height=self.resize_height,
            generate_thumbnail=self.generate_thumbnail,
            thumbnail_width=self.thumb_width,
            thumbnail_height=self.thumb_height
        )
        response = self.stub.ProcessImage(request)

        if response.message != "Success":
            print(f"Error from server: {response.message}")
            return

        # Save and open final processed image
        processed_filename = "final_processed_image.png"
        with open(processed_filename, "wb") as f:
            f.write(response.processed_image)

        print(f"Processed image saved as '{processed_filename}'")
        os.startfile(processed_filename)

        # Save and open thumbnail if generated
        if self.generate_thumbnail and response.thumbnail_image:
            thumbnail_filename = "final_thumbnail.png"
            with open(thumbnail_filename, "wb") as f:
                f.write(response.thumbnail_image)

            print(f"Thumbnail saved as '{thumbnail_filename}'")
            os.startfile(thumbnail_filename)

    def interactive_loop(self):
        """Run an interactive loop to allow the user to apply transformations."""
        image_path = input("Enter the image file path: ").strip()
        self.load_image(image_path)

        while True:
            print("\nAvailable operations:")
            print("1. Flip Horizontal")
            print("2. Flip Vertical")
            print("3. Rotate (custom degrees)")
            print("4. Convert to Grayscale")
            print("5. Resize")
            print("6. Generate Thumbnail")
            print("7. Rotate Left (-90°)")
            print("8. Rotate Right (90°)")
            print("Type 'done' to finish and process the image.")

            choice = input("Enter operation number (or 'done' to finish): ").strip()

            if choice.lower() == "done":
                break
            elif choice == "1":
                self.operations.append("flip_horizontal")
            elif choice == "2":
                self.operations.append("flip_vertical")
            elif choice == "3":
                self.rotate_degrees = int(input("Enter degrees to rotate: "))
                self.operations.append("rotate")
            elif choice == "4":
                self.operations.append("grayscale")
            elif choice == "5":
                self.resize_width = int(input("Enter new width: "))
                self.resize_height = int(input("Enter new height: "))
                self.operations.append("resize")
            elif choice == "6":
                self.generate_thumbnail = True
                while True:
                    thumbnail_choice = input("Use default size (300x300)? (yes/no): ").strip().lower()

                    if thumbnail_choice == "yes":
                        self.thumb_width, self.thumb_height = 300, 300
                        break
                    elif thumbnail_choice == "no":
                        try:
                            self.thumb_width = int(input("Enter thumbnail width: "))
                            self.thumb_height = int(input("Enter thumbnail height: "))
                            break
                        except ValueError:
                            print("Invalid input! Please enter valid numbers for width and height.")
                    else:
                        print("Invalid input! Please enter 'yes' or 'no'.")
            elif choice == "7":
                self.rotate_degrees = -90
                self.operations.append("rotate")
            elif choice == "8":
                self.rotate_degrees = 90
                self.operations.append("rotate")
            else:
                print("Invalid choice! Please try again.")
                continue

        # Perform image processing in one API call
        self.process_image()


if __name__ == "__main__":
    client = GrpcImageClient()
    client.interactive_loop()
