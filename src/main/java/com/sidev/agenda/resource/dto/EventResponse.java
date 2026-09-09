package com.sidev.agenda.resource.dto;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;

import java.time.LocalDateTime;
import java.util.UUID;

public record EventResponse(UUID id, String title, LocalDateTime start, LocalDateTime end, EventCategory category) {

    public static EventResponse from(Event event) {
        return new EventResponse(event.id(), event.title(), event.start(), event.end(), event.category());
    }
}
