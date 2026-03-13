package com.example.tour.util;

import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class FileUploadUtil {

    public static String saveFile(MultipartFile file, String uploadDir) throws Exception {
        if (file == null || file.isEmpty()) {
            return null;
        }

        File dir = new File(uploadDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        String originalName = file.getOriginalFilename();
        String uuid = UUID.randomUUID().toString();
        String fileName = uuid + "_" + originalName;

        File target = new File(dir, fileName);
        file.transferTo(target);

        return fileName;
    }

    public static void deleteFile(String fileName, String uploadPath) {
        if (fileName != null && uploadPath != null) {
            Path path = Paths.get(uploadPath, fileName);
            try {
                Files.deleteIfExists(path);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}