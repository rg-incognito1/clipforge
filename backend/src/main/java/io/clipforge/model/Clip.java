package io.clipforge.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDateTime;

@Entity
@Table(name = "clips")
@Data
@NoArgsConstructor
public class Clip {

    @Id
    @UuidGenerator
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "job_id", nullable = false)
    private Job job;

    private Double startSeconds;
    private Double endSeconds;
    private Double duration;
    private String momentType;
    private Integer viralScore;

    @Column(columnDefinition = "TEXT")
    private String outputPath;

    private String storylineTitle;

    @Column(columnDefinition = "TEXT")
    private String storylineSummary;

    @CreationTimestamp
    private LocalDateTime createdAt;
}
