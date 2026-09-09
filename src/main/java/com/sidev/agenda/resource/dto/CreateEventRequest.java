package com.sidev.agenda.resource.dto;

import com.sidev.agenda.model.EventCategory;

import java.time.LocalDateTime;

public record CreateEventRequest(String title, LocalDateTime start, LocalDateTime end, EventCategory category) {
}
