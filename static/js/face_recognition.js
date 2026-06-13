(function () {
  "use strict";

  const video = document.getElementById("webcam-feed");
  const canvas = document.getElementById("webcam-canvas");
  const startBtn = document.getElementById("start-recognition");
  const stopBtn = document.getElementById("stop-recognition");
  const statusBadge = document.getElementById("recognition-status");
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const recognizeUrl = startBtn.dataset.recognizeUrl;
  const subjectId = startBtn.dataset.subjectId;

  let stream = null;
  let captureInterval = null;
  let ctx = null;
  let isRunning = false;

  function setStatus(text, colorClass) {
    statusBadge.textContent = text;
    statusBadge.className = "badge " + colorClass;
  }

  function drawBoxes(faces) {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    faces.forEach(function (face) {
      var x = face.box[0];
      var y = face.box[1];
      var w = face.box[2];
      var h = face.box[3];
      ctx.strokeStyle = face.matched ? "#1E8A5E" : "#DC3545";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, w, h);
      if (face.name) {
        ctx.fillStyle = face.matched ? "#1E8A5E" : "#DC3545";
        ctx.font = "13px Poppins, sans-serif";
        ctx.fillText(face.name, x, y > 16 ? y - 6 : y + h + 14);
      }
    });
  }

  function updateStudentRow(studentId, matchedName) {
    var row = document.querySelector(
      '[data-student-id="' + studentId + '"]'
    );
    if (!row) return;
    var presentRadio = row.querySelector('input[value="Present"]');
    if (presentRadio) {
      presentRadio.checked = true;
      presentRadio.dispatchEvent(new Event("change"));
    }
    var pill = row.querySelector(".status-pill");
    if (pill) {
      pill.textContent = "Present (auto)";
      pill.className = "badge bg-success status-pill";
    }
  }

  function captureAndRecognize() {
    if (!video || video.readyState < 2) return;

    var offscreen = document.createElement("canvas");
    offscreen.width = video.videoWidth || 640;
    offscreen.height = video.videoHeight || 480;
    var offCtx = offscreen.getContext("2d");
    offCtx.drawImage(video, 0, 0, offscreen.width, offscreen.height);
    var frameData = offscreen.toDataURL("image/jpeg", 0.8);

    fetch(recognizeUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        frame: frameData,
        subject_id: subjectId,
      }),
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Server returned " + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        if (data.error) {
          setStatus("Error: " + data.error, "bg-danger text-white");
          return;
        }

        var matched = data.matched_students || [];
        var faces = data.faces || [];

        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        drawBoxes(faces);

        if (matched.length > 0) {
          setStatus(
            matched.length + " student(s) recognised",
            "bg-success text-white"
          );
          matched.forEach(function (s) {
            updateStudentRow(s.student_id, s.name);
          });
        } else {
          setStatus("Scanning...", "bg-primary text-white");
        }
      })
      .catch(function (err) {
        console.error("Face recognition error:", err);
        setStatus("Connection error", "bg-warning text-dark");
      });
  }

  function startRecognition() {
    if (isRunning) return;

    navigator.mediaDevices
      .getUserMedia({ video: { width: 640, height: 480 }, audio: false })
      .then(function (mediaStream) {
        stream = mediaStream;
        video.srcObject = stream;
        video.play();

        ctx = canvas.getContext("2d");
        isRunning = true;

        startBtn.disabled = true;
        stopBtn.disabled = false;
        setStatus("Scanning...", "bg-primary text-white");

        video.addEventListener(
          "loadedmetadata",
          function () {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
          },
          { once: true }
        );

        captureInterval = setInterval(captureAndRecognize, 1000);
      })
      .catch(function (err) {
        console.error("Webcam error:", err);
        if (err.name === "NotAllowedError") {
          setStatus("Camera permission denied", "bg-danger text-white");
        } else if (err.name === "NotFoundError") {
          setStatus("No camera found", "bg-danger text-white");
        } else {
          setStatus("Camera unavailable", "bg-danger text-white");
        }
        showFallback();
      });
  }

  function stopRecognition() {
    if (captureInterval) {
      clearInterval(captureInterval);
      captureInterval = null;
    }
    if (stream) {
      stream.getTracks().forEach(function (track) {
        track.stop();
      });
      stream = null;
    }
    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    video.srcObject = null;
    isRunning = false;

    startBtn.disabled = false;
    stopBtn.disabled = true;
    setStatus("Stopped", "bg-secondary text-white");
  }

  function showFallback() {
    var fallback = document.getElementById("manual-fallback-notice");
    if (fallback) {
      fallback.classList.remove("d-none");
    }
  }

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus("Webcam not supported", "bg-danger text-white");
    startBtn.disabled = true;
    showFallback();
  }

  startBtn.addEventListener("click", startRecognition);
  stopBtn.addEventListener("click", stopRecognition);

  window.addEventListener("beforeunload", function () {
    if (isRunning) stopRecognition();
  });
})();