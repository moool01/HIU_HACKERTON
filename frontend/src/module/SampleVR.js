import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

// 라벨 파싱 함수
function parseLabels(text) {
  return text
    .trim()
    .split('\n')
    .map((line) => {
      const [cls, yaw, pitch, w, h] = line.split(' ').map(Number);
      return { cls, yaw, pitch, w, h };
    });
}

function isInsideBox(yaw, pitch, box) {
  const { yaw: byaw, pitch: bpitch, w, h } = box;
  return Math.abs(yaw - byaw) < w / 2 && Math.abs(pitch - bpitch) < h / 2;
}

const SampleVR = () => {
  const pannellumRef = useRef(null);
  const [boxes, setBoxes] = useState([]);
  const navigate = useNavigate();



  useEffect(() => {
    if (!window.pannellum) return;
    const viewer = window.pannellum.viewer('sampleVR-pan', {
      type: "equirectangular",
      panorama: process.env.PUBLIC_URL + "/result/sampleVR.jpg", // VR 이미지 경로(2:1 비율 VR 이미지)
      autoLoad: true,
      hfov: 120,
      minHfov: 60,
      maxHfov: 140,
      pitch: 0,
      yaw: 0,
      compass: true,
      autoRotate: 0,
      minPitch: -50, // 아래로 최대 각도 (기본값: -90)
      maxPitch: 50,  // 위로 최대 각도 (기본값: 90)
    });

    let downCoords = null;

    viewer.on('mousedown', function (e) {
      downCoords = viewer.mouseEventToCoords(e);
    });

    viewer.on('mouseup', function (e) {
      const upCoords = viewer.mouseEventToCoords(e);
      if (!downCoords || !upCoords) return;
      const [upPitch, upYaw] = upCoords;
      let found = false;
    });

    // cleanup
    return () => {
      const panDiv = document.getElementById('sampleVR-pan');
      if (panDiv) panDiv.innerHTML = '';
    };
  }, [boxes, navigate]);

  return (
    <div>
      <div
        id="sampleVR-pan"
        ref={pannellumRef}
        style={{ width: '100%', height: '500px', border: '2px solid #aaa' }}
      />
    </div>
  );
};

export default SampleVR;