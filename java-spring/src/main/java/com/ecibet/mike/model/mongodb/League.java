package com.ecibet.mike.model.mongodb;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "leagues")
public class League {

    @Id
    private String id;

    @Indexed(unique = true)
    private String externalId;

    private String name;
    private String alternateName;

    private String sport;
    private String country;

    private String website;
    private String facebook;
    private String instagram;
    private String twitter;
    private String youtube;

    private String description;

    private String logo;
    private String badge;
    private String trophy;

    private Integer formedYear;
    private String currentSeason;

    private List<String> seasons;
    private List<String> teams;

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}