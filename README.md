# DIVOOM PIXOO64

```bash
divoom_pixoo:
  ip_address: 192.168.0.12
  scan_interval:
    seconds: 60
  pages:
    - page: 1
      texts:
        - text: "BIG TEXT"
          font_color: "{{ [255, 255, 255] }}"
          position: [3, 20]
          font: big
        - text: "Normal"
          font_color: "{{ [255, 255, 255] }}"
          position: [3, 28]
      images:
        - image: "config/custom_components/divoom_pixoo/img/industry.png"
          position: [3, 40]
```