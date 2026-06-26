package io.clipforge.repository;

import io.clipforge.model.Clip;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ClipRepository extends JpaRepository<Clip, String> {
    List<Clip> findByJobId(String jobId);
}
