package io.clipforge.controller;

import io.clipforge.model.Clip;
import io.clipforge.model.Job;
import io.clipforge.model.JobStatus;
import io.clipforge.service.JobService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * Internal endpoints called by Python workers — not exposed to end users.
 */
@RestController
@RequestMapping("/internal")
@RequiredArgsConstructor
public class InternalController {

    private final JobService jobService;

    @GetMapping("/jobs/{id}")
    public ResponseEntity<Map<String, Object>> getJobDetail(@PathVariable String id) {
        Job job = jobService.getJob(id);
        return ResponseEntity.ok(Map.of(
                "id", job.getId(),
                "videoPath", job.getVideoPath() != null ? job.getVideoPath() : "",
                "videoName", job.getVideoName() != null ? job.getVideoName() : "",
                "recipe", job.getRecipe(),
                "formats", job.getFormats(),
                "status", job.getStatus().name()
        ));
    }

    @PostMapping("/jobs/{id}/status")
    public ResponseEntity<Void> updateStatus(
            @PathVariable String id,
            @RequestBody Map<String, String> body) {

        JobStatus status = JobStatus.valueOf(body.get("status"));
        String error = body.get("errorMessage");
        jobService.updateStatus(id, status, error);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/jobs/{id}/clips")
    public ResponseEntity<Map<String, String>> addClip(
            @PathVariable String id,
            @RequestBody Map<String, Object> body) {

        Clip clip = new Clip();
        clip.setStartSeconds(toDouble(body.get("startSeconds")));
        clip.setEndSeconds(toDouble(body.get("endSeconds")));
        clip.setDuration(toDouble(body.get("duration")));
        clip.setMomentType((String) body.get("momentType"));
        clip.setViralScore(toInt(body.get("viralScore")));
        clip.setOutputPath((String) body.get("outputPath"));
        clip.setStorylineTitle((String) body.get("storylineTitle"));
        clip.setStorylineSummary((String) body.get("storylineSummary"));

        Clip saved = jobService.addClip(id, clip);
        return ResponseEntity.ok(Map.of("clipId", saved.getId()));
    }

    private Double toDouble(Object v) {
        return v instanceof Number n ? n.doubleValue() : 0.0;
    }

    private Integer toInt(Object v) {
        return v instanceof Number n ? n.intValue() : 0;
    }
}
