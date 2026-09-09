package com.sidev.agenda.service;

import com.sidev.agenda.model.Event;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Gestion en memoire des evenements de l'agenda.
 * Un depot en memoire suffit pour la demo : le sujet de la conference est la couverture
 * de tests, pas la persistance.
 */
@ApplicationScoped
public class EventService {

    private final Map<UUID, Event> events = new ConcurrentHashMap<>();

    @Inject
    ConflictDetector conflictDetector;

    public Event create(Event candidate) {
        Event toStore = candidate.id() == null ? candidate.withId(UUID.randomUUID()) : candidate;

        boolean conflict = events.values().stream()
                .anyMatch(existing -> conflictDetector.isConflicting(existing, toStore));
        if (conflict) {
            throw new EventConflictException(
                    "L'evenement '" + toStore.title() + "' chevauche un evenement deja planifie");
        }

        events.put(toStore.id(), toStore);
        return toStore;
    }

    public List<Event> findByDate(LocalDate date) {
        return events.values().stream()
                .filter(event -> event.start().toLocalDate().equals(date))
                .sorted(Comparator.comparing(Event::start))
                .toList();
    }

    public List<Event> findAll() {
        return new ArrayList<>(events.values());
    }

    public boolean delete(UUID id) {
        return events.remove(id) != null;
    }
}
