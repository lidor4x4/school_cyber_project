
"""
    def send_audio(self):
        def callback(indata, frames, time, status):
            self.audio_udp.sendto(indata.tobytes(), (self.server_ip, AUDIO_PORT))
        with sd.InputStream(channels=1, samplerate=44100, callback=callback):
            while True:
                sd.sleep(1000)

    def receive_audio(self):
        stream = sd.OutputStream(channels=1, samplerate=44100)
        stream.start()
        while True:
            data, _ = self.audio_udp.recvfrom(4096)
            stream.write(np.frombuffer(data, dtype=np.float32))
"""