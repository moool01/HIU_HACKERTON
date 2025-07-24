import React, { useEffect, useState } from "react";

const GRID_SIZE = 25;

const itemColors = {
  room1: "#cce5ff",
  room2: "#d4edda",
  room3: "#fff3cd",
  room4: "#f8d7da",
  room5: "#e2e3e5",
  room6: "#d1c4e9",
};

const cellStyle = {
  width: 40,
  height: 65,
  border: "1px solid #ccc",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "10px",
};

const UploadPage = () => {
  const [roomMap, setRoomMap] = useState({});
  const [roomCenters, setRoomCenters] = useState({});
  const [roomNames, setRoomNames] = useState({});
  const [roomImages, setRoomImages] = useState({});

  // 1. 초기 roomMap 불러오기
  useEffect(() => {
  const saved = localStorage.getItem("roomMap");
  if (!saved) return;

  const parsed = JSON.parse(saved);
  setRoomMap(parsed);

  const roomToCells = {};
  for (const key in parsed) {
    const room = parsed[key];
    if (!roomToCells[room]) roomToCells[room] = [];
    roomToCells[room].push(key);
  }

  const centers = {};
  const names = {};

  for (const room in roomToCells) {
    const cells = roomToCells[room];

    // ✅ 중심 좌표 계산
    const coords = cells.map((key) => {
      const [x, y] = key.split(",").map(Number);
      return { x, y };
    });

    const avgX = Math.round(
      coords.reduce((sum, c) => sum + c.x, 0) / coords.length
    );
    const avgY = Math.round(
      coords.reduce((sum, c) => sum + c.y, 0) / coords.length
    );

    const centerKey = `${avgX},${avgY}`;
    centers[room] = centerKey;

    names[room] = room.replace("room", "방 ");
  }

  setRoomCenters(centers);
  setRoomNames(names);
}, []);


  // 2. 방 이름 변경
  const handleNameChange = (room, newName) => {
    setRoomNames((prev) => ({
      ...prev,
      [room]: newName,
    }));
  };

  // 3. 이미지 업로드
  const handleImageUpload = (room, file) => {
    setRoomImages((prev) => ({
      ...prev,
      [room]: file,
    }));
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>
      <h2>📋 방 이름 수정 & 이미지 업로드</h2>
      <div>
        {Array.from({ length: GRID_SIZE }).map((_, y) => (
          <div key={y} style={{ display: "flex" }}>
            {Array.from({ length: GRID_SIZE }).map((_, x) => {
              const key = `${x},${y}`;
              const room = roomMap[key];
              const isCenter = room && roomCenters[room] === key;
              const bgColor = room ? itemColors[room] : "#fff";

              return (
                <div key={key} style={{ ...cellStyle, backgroundColor: bgColor }}>
                  {room && (
                    <>
                      {isCenter ? (
                        <>
                          {/* 이름 수정 input */}
                          <input
                            value={roomNames[room] || ""}
                            onChange={(e) =>
                              handleNameChange(room, e.target.value)
                            }
                            style={{ width: "90%", fontSize: "10px", marginBottom: "3px" }}
                          />
                          {/* 이미지 업로드 */}
                          <input
                            type="file"
                            accept="image/*"
                            onChange={(e) =>
                              handleImageUpload(room, e.target.files[0])
                            }
                            style={{ fontSize: "9px" }}
                          />
                          {/* 미리보기 */}
                          {roomImages[room] && (
                            <img
                              src={URL.createObjectURL(roomImages[room])}
                              alt="preview"
                              style={{
                                width: "100%",
                                height: "28px",
                                objectFit: "cover",
                                marginTop: "2px",
                              }}
                            />
                          )}
                        </>
                      ) : (
                        <div>{roomNames[room]}</div>
                      )}
                    </>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

export default UploadPage;
