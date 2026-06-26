package io.clipforge.controller;

import io.clipforge.model.Clip;
import io.clipforge.model.Job;
import io.clipforge.service.JobService;
import io.clipforge.service.StorageService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/jobs")
@RequiredArgsConstructor
public class JobController {

    private final JobService jobService;
    private final StorageService storageService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<Map<String, Object>> createJob(
            @RequestParam("file") MultipartFile file,
            @RequestParam(defaultValue = "mrbeast") String recipe,
            @RequestParam(defaultValue = "9:16") String formats) throws IOException {

        Job job = jobService.createJob(file, recipe, formats);
        return ResponseEntity.ok(Map.of(
                "jobId", job.getId(),
                "status", job.getStatus().name(),
                "videoName", job.getVideoName() != null ? job.getVideoName() : ""
        ));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getJob(@PathVariable String id) {
        Job job = jobService.getJob(id);
        List<Clip> clips = jobService.getClips(id);
        return ResponseEntity.ok(toJobResponse(job, clips));
    }

    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listJobs() {
        return ResponseEntity.ok(
                jobService.listJobs().stream()
                        .map(j -> toJobResponse(j, jobService.getClips(j.getId())))
                        .toList()
        );
    }

    @GetMapping("/{jobId}/clips/{clipId}/stream")
    public ResponseEntity<Resource> streamClip(
            @PathVariable String jobId,
            @PathVariable String clipId) {
        return serveClip(clipId, false);
    }

    @GetMapping("/{jobId}/clips/{clipId}/download")
    public ResponseEntity<Resource> downloadClip(
            @PathVariable String jobId,
            @PathVariable String clipId) {
        return serveClip(clipId, true);
    }

    private ResponseEntity<Resource> serveClip(String clipId, boolean asAttachment) {
        Clip clip = jobService.getClip(clipId);
        Path clipPath = storageService.resolveClipPath(clip.getOutputPath());
        Resource resource = new FileSystemResource(clipPath);

        if (!resource.exists()) {
            return ResponseEntity.notFound().build();
        }

        var builder = ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("video/mp4"));

        if (asAttachment) {
            builder.header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\"" + clipPath.getFileName() + "\"");
        }

        return builder.body(resource);
    }

    private Map<String, Object> toJobResponse(Job job, List<Clip> clips) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", job.getId());
        map.put("status", job.getStatus().name());
        map.put("recipe", job.getRecipe());
        map.put("formats", job.getFormats());
        map.put("videoName", job.getVideoName() != null ? job.getVideoName() : "");
        map.put("errorMessage", job.getErrorMessage() != null ? job.getErrorMessage() : "");
        map.put("createdAt", job.getCreatedAt() != null ? job.getCreatedAt().toString() : "");
        map.put("clips", clips.stream().map(this::toClipResponse).toList());
        return map;
    }

    private Map<String, Object> toClipResponse(Clip clip) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", clip.getId());
        map.put("startSeconds", clip.getStartSeconds() != null ? clip.getStartSeconds() : 0.0);
        map.put("endSeconds", clip.getEndSeconds() != null ? clip.getEndSeconds() : 0.0);
        map.put("duration", clip.getDuration() != null ? clip.getDuration() : 0.0);
        map.put("momentType", clip.getMomentType() != null ? clip.getMomentType() : "");
        map.put("viralScore", clip.getViralScore() != null ? clip.getViralScore() : 0);
        map.put("storylineTitle", clip.getStorylineTitle() != null ? clip.getStorylineTitle() : "");
        map.put("storylineSummary", clip.getStorylineSummary() != null ? clip.getStorylineSummary() : "");
        return map;
    }
}
