# ADR-008: Build the heatmap with IDW

The backend derives a compact inverse-distance-weighted grid from weather samples. The client recolors that same grid for wind, rain, snow, and overall-risk layers without another network request.
