package io.clipforge.repository;

import io.clipforge.model.Job;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface JobRepository extends JpaRepository<Job, String> {
    List<Job> findAllByOrderByCreatedAtDesc();
}
