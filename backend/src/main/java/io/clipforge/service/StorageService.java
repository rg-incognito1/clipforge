package io.clipforge.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
public class StorageService {

    @Value("${storage.path:/storage}")
    private String storagePath;

    public String saveUpload(MultipartFile file, String jobId) throws IOException {
        Path uploadDir = Paths.get(storagePath, "uploads", jobId);
        Files.createDirectories(uploadDir);

        String filename = (file.getOriginalFilename() != null && !file.getOriginalFilename().isBlank())
                ? file.getOriginalFilename()
                : "input.mp4";

        Path dest = uploadDir.resolve(filename);
        file.transferTo(dest.toFile());
        return dest.toString();
    }

    public Path resolveClipPath(String outputPath) {
        return Paths.get(outputPath);
    }
}
