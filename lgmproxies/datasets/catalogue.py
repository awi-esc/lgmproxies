from .datamanager import register_dataset

def register_coast(res):
    return register_dataset(f"naturalearth/ne_{res}_coastline",
        f"https://naturalearth.s3.amazonaws.com/{res}_physical/ne_{res}_coastline.zip", ext=".zip")
        # f"https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/{res}/physical/ne_{res}_coastline.zip", ext=".zip")

def register_land(res):
    return register_dataset(f"naturalearth/ne_{res}_land",
        f"https://naturalearth.s3.amazonaws.com/{res}_physical/ne_{res}_land.zip", ext=".zip")
        # f"https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/{res}/physical/ne_{res}_land.zip", ext=".zip")

require_coast_110m = register_coast("110m")
require_land_50m = register_land("50m")