
import sys, os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from necbol.nec_wrapper import NECModel
from necbol import geometry_builder
from necbol import GUI_builder


model = NECModel(working_dir="..\\nec_wkg",
                 model_name = "New",
                 nec_exe_path="C:\\4nec2\\exe\\nec2dxs11k.exe",
                 verbose=False)
model.set_wire_conductivity(sigma = 58000000)
model.set_frequency(MHz = 144.2)
model.set_gain_point(azimuth = 90, elevation = 3)
model.set_ground(eps_r = 11, sigma = 0.01, origin_height_m = 8.0)
model.start_geometry()
antenna_components = geometry_builder.components()
#model.write_nec()

print(model.model_text)

GUI_builder.build(model,  antenna_components, title = model.model_name)


print("Done")


