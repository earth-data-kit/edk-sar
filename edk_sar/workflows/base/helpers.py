# helper functions for coregistration/interferograms workflows

# Things like geocode() function. 
# geocode() will be used to geocode different outputs of interferograms or coregistration
# It will take .vrt, lon.rdr, lat.rdr and output path as input. 
# It will add the GEOLOCATION metadata and save it as a new output file
# It will also check if lon.rdr, lat.rdr and input vrt have same dimensions, if not it should raise an error

# convert_to_cog() will be used to convert .vrt to .cog
# It will take .vrt and output path as input. 
# It will convert .vrt to .cog and save it as a new output file