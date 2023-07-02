import cv2
import numpy as np
import matplotlib.pyplot as plt
from databases import Employee, Databases

database = Databases()


def plot_employee_faces(database: Databases):
    employees = database.get_all_employess()
    num_employees = len(employees)

    fig, axs = plt.subplots(1, num_employees, figsize=(12, 6))

    face_image_rgb = None  # Define face_image_rgb

    if num_employees == 1:
        face_image = cv2.imdecode(
            np.frombuffer(employees[0].faces, np.uint8), cv2.IMREAD_COLOR
        )
        face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        axs.imshow(face_image_rgb)
        axs.set_title(employees[0].name)
        axs.axis("off")
    else:
        for i, employee in enumerate(employees):
            face_image = cv2.imdecode(
                np.frombuffer(employee.faces, np.uint8), cv2.IMREAD_COLOR
            )
            face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

            axs[i].imshow(face_image_rgb)
            axs[i].set_title(employee.name)
            axs[i].axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_employee_faces(database)
