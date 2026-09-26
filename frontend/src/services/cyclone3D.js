export function build3DCyclone(cx, cy, maxRadiusDeg = 1.5, angleOffset = 0) {
  const features = [];
  const arms = 5;
  const pointsPerArm = 40;
  
  for (let arm = 0; arm < arms; arm++) {
    const armOffset = (Math.PI * 2 / arms) * arm + angleOffset;
    
    for (let i = 2; i < pointsPerArm; i++) {
      // 0 to 1
      const t = i / pointsPerArm;
      
      // Radius increases non-linearly
      const r = maxRadiusDeg * Math.pow(t, 1.2);
      
      // Angle spirals outwards
      const angle = armOffset + (t * Math.PI * 3); // 1.5 rotations
      
      const px = cx + r * Math.cos(angle);
      // Adjust for mercator distortion approximately
      const py = cy + (r * Math.sin(angle)) / Math.cos(cy * Math.PI / 180);
      
      // Height calculation:
      // Eyewall is highest (t between 0.05 and 0.15)
      let height = 1000;
      if (t < 0.1) {
        height = 12000 * (t / 0.1);
      } else if (t < 0.2) {
        height = 12000 - 4000 * ((t - 0.1) / 0.1);
      } else {
        height = 8000 * (1 - t) + Math.random() * 2000;
      }
      
      // Opacity / color
      const intensity = 1 - t;
      
      // Generate a small hexagon or quad at px, py
      const polyRadius = 0.02 + 0.04 * t;
      const coords = [];
      for(let a=0; a<6; a++) {
        const pa = (Math.PI * 2 / 6) * a;
        coords.push([
          px + polyRadius * Math.cos(pa),
          py + polyRadius * Math.sin(pa) / Math.cos(cy * Math.PI / 180)
        ]);
      }
      coords.push(coords[0]); // close ring
      
      features.push({
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [coords]
        },
        properties: {
          height: height,
          base: height * 0.8,
          intensity: intensity
        }
      });
    }
  }
  
  return {
    type: 'FeatureCollection',
    features: features
  };
}
