package io.clipforge.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "jobs")
@Data
@NoArgsConstructor
public class Job {

    @Id
    @UuidGenerator
    private String id;

    @Column(columnDefinition = "TEXT")
    private String videoPath;

    private String videoName;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private JobStatus status = JobStatus.QUEUED;

    @Column(nullable = false)
    private String recipe = "mrbeast";

    @Column(nullable = false)
    private String formats = "9:16";

    @Column(columnDefinition = "TEXT")
    private String errorMessage;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "job", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Clip> clips = new ArrayList<>();

    public Job(String videoPath, String videoName, String recipe, String formats) {
        this.videoPath = videoPath;
        this.videoName = videoName;
        this.recipe = recipe;
        this.formats = formats;
    }
}
