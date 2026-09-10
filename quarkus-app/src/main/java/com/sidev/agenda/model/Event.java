package com.sidev.agenda.model;

import java.time.LocalDateTime;
import java.util.UUID;

public record Event(UUID id, String title, LocalDateTime start, LocalDateTime end, EventCategory category) {

    public Event {
        if (title == null || title.isBlank()) {
            throw new IllegalArgumentException("Le titre de l'evenement est obligatoire");
        }
        if (start == null || end == null) {
            throw new IllegalArgumentException("La date de debut et de fin sont obligatoires");
        }
        if (!end.isAfter(start)) {
            throw new IllegalArgumentException("La date de fin doit etre apres la date de debut");
        }
    }

    public Event withId(UUID newId) {
        return new Event(newId, title, start, end, category);
    }
}
