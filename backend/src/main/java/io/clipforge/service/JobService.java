package io.clipforge.service;

import io.clipforge.model.Clip;
import io.clipforge.model.Job;
import io.clipforge.model.JobStatus;
import io.clipforge.repository.ClipRepository;
import io.clipforge.repository.JobRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
public class JobService {

    private static final String QUEUE_KEY = "clipforge:job_queue";

    private final JobRepository jobRepository;
    private final ClipRepository clipRepository;
    private final StorageService storageService;
    private final StringRedisTemplate redisTemplate;

    @Transactional
    public Job createJob(MultipartFile file, String recipe, String formats) throws IOException {
        Job job = new Job(null, file.getOriginalFilename(), recipe, formats);
        job = jobRepository.save(job);

        String videoPath = storageService.saveUpload(file, job.getId());
        job.setVideoPath(videoPath);
        job = jobRepository.save(job);

        redisTemplate.opsForList().leftPush(QUEUE_KEY, job.getId());
        return job;
    }

    public Job getJob(String id) {
        return jobRepository.findById(id)
                .orElseThrow(() -> new NoSuchElementException("Job not found: " + id));
    }

    public List<Job> listJobs() {
        return jobRepository.findAllByOrderByCreatedAtDesc();
    }

    @Transactional
    public void updateStatus(String jobId, JobStatus status, String errorMessage) {
        Job job = getJob(jobId);
        job.setStatus(status);
        if (errorMessage != null) {
            job.setErrorMessage(errorMessage);
        }
        jobRepository.save(job);
    }

    @Transactional
    public Clip addClip(String jobId, Clip clip) {
        Job job = getJob(jobId);
        clip.setJob(job);
        return clipRepository.save(clip);
    }

    public List<Clip> getClips(String jobId) {
        return clipRepository.findByJobId(jobId);
    }

    public Clip getClip(String clipId) {
        return clipRepository.findById(clipId)
                .orElseThrow(() -> new NoSuchElementException("Clip not found: " + clipId));
    }
}
