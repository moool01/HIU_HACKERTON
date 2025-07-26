const express = require('express');
const multer = require('multer');
const path = require('path');
const cors = require('cors');
const fs = require('fs');

const app = express();
const PORT = 3001;

// CORS 허용
app.use(cors());
app.use(express.json());

// src/data 폴더 생성
const uploadDir = path.join(__dirname, '../frontend/src/data');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// multer 설정
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const roomType = req.body.roomType || 'unknown';
    const timestamp = Date.now();
    const ext = path.extname(file.originalname);
    cb(null, `${roomType}_${timestamp}${ext}`);
  },
});
const upload = multer({ storage: storage });

// 파일 업로드 API
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, error: '파일이 없습니다.' });
  }
  res.json({
    success: true,
    filename: req.file.filename,
    path: req.file.path,
    originalName: req.file.originalname,
  });
});

// 파일 삭제 API
app.delete('/api/delete', (req, res) => {
  const { filename } = req.body;
  if (!filename) {
    return res
      .status(400)
      .json({ success: false, error: '파일명이 필요합니다.' });
  }
  const filePath = path.join(uploadDir, filename);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    return res.json({ success: true });
  } else {
    return res
      .status(404)
      .json({ success: false, error: '파일을 찾을 수 없습니다.' });
  }
});
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, error: '파일이 없습니다.' });
  }

  // 중복 파일 체크
  const uploadDir = path.join(__dirname, '../frontend/src/data');
  const filename = req.file.filename;
  const filePath = path.join(uploadDir, filename);

  if (fs.existsSync(filePath)) {
    // 이미 파일이 있으면 삭제하지 않고 업로드 거부
    // 업로드된 파일은 multer가 임시로 저장하므로 삭제 필요
    fs.unlinkSync(req.file.path);
    return res
      .status(409)
      .json({ success: false, error: '이미 같은 이름의 파일이 존재합니다.' });
  }

  res.json({
    success: true,
    filename: req.file.filename,
    path: req.file.path,
    originalName: req.file.originalname,
  });
});

app.listen(PORT, () => {
  console.log(`백엔드 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
});