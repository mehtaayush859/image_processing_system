
import grpc
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageOps
import io
import image_processor_pb2
import image_processor_pb2_grpc


class ImageProcessor:
    def __init__(self, request):
        self.request = request
        self.image = None
        self.intermediate_images = []

    def process_image(self):
        try:
            # Load image from bytes
            self.image = Image.open(io.BytesIO(self.request.image_data))

            # Apply transformations in the given order
            for operation in self.request.operations:
                print(f"Applying operation: {operation}")
                self._apply_operation(operation)

            # Convert processed image to bytes
            processed_image_bytes = self._image_to_bytes(self.image)

            # Handle thumbnail processing
            thumbnail_bytes = b""
            if self.request.generate_thumbnail:
                thumbnail_bytes = self._generate_thumbnail(self.image)

            return image_processor_pb2.ImageResponse(
                processed_image=processed_image_bytes,
                thumbnail_image=thumbnail_bytes,
                message="Success",
                intermediate_images=self.intermediate_images
            )
        except Exception as e:
            return image_processor_pb2.ImageResponse(
                message=f"Error processing image on server side: {str(e)}"
            )

    def _apply_operation(self, operation):
        intermediate_image = self.image.copy()

        if operation == "flip_horizontal":
            intermediate_image = ImageOps.mirror(intermediate_image)
        elif operation == "flip_vertical":
            intermediate_image = ImageOps.flip(intermediate_image)
        elif operation == "rotate":
            intermediate_image = intermediate_image.rotate(self.request.rotate_degrees, expand=True)
        elif operation == "grayscale":
            intermediate_image = ImageOps.grayscale(intermediate_image)
        elif operation == "resize":
            if self.request.resize_width > 0 and self.request.resize_height > 0:
                intermediate_image = intermediate_image.resize(
                    (self.request.resize_width, self.request.resize_height)
                )

        # Save intermediate image for visualization
        self._store_intermediate_image(intermediate_image)

        # Update the main image after the operation
        self.image = intermediate_image

    def _store_intermediate_image(self, intermediate_image):
        intermediate_image_byte_arr = io.BytesIO()
        intermediate_image.save(intermediate_image_byte_arr, format="PNG")
        intermediate_image_bytes = intermediate_image_byte_arr.getvalue()
        self.intermediate_images.append(intermediate_image_bytes)

    def _image_to_bytes(self, image):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def _generate_thumbnail(self, image):
        thumbnail = image.copy()
        thumb_width = self.request.thumbnail_width if self.request.thumbnail_width > 0 else 30
        thumb_height = self.request.thumbnail_height if self.request.thumbnail_height > 0 else 30
        thumbnail.thumbnail((thumb_width, thumb_height))
        return self._image_to_bytes(thumbnail)


class ImageProcessorServicer(image_processor_pb2_grpc.ImageProcessorServicer):
    def ProcessImage(self, request, context):
        image_processor = ImageProcessor(request)
        return image_processor.process_image()

    @staticmethod
    def serve():
        server = grpc.server(ThreadPoolExecutor(max_workers=10))
        image_processor_pb2_grpc.add_ImageProcessorServicer_to_server(ImageProcessorServicer(), server)
        server.add_insecure_port("[::]:50051")
        server.start()
        print("Server is running on port 50051...")
        server.wait_for_termination()


if __name__ == "__main__":
    ImageProcessorServicer.serve()
