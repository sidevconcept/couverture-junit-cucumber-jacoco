package com.sidev.agenda.resource;

import com.sidev.agenda.model.Event;
import com.sidev.agenda.model.EventCategory;
import com.sidev.agenda.resource.dto.CreateEventRequest;
import com.sidev.agenda.resource.dto.DayViewResponse;
import com.sidev.agenda.resource.dto.EventResponse;
import com.sidev.agenda.resource.dto.RecurrenceRequest;
import com.sidev.agenda.service.EventConflictException;
import com.sidev.agenda.service.EventService;
import com.sidev.agenda.service.HolidayService;
import com.sidev.agenda.service.QuoteOfTheDayService;
import com.sidev.agenda.service.RecurrenceService;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.NotFoundException;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

/**
 * Meme API que com.sidev.agenda.resource.CalendarResource du module quarkus-app,
 * portee sur Cassini (Jakarta REST 4.0 sur Chappe). Difference notable : le
 * conflit d'horaire est intercepte ici directement dans la methode plutot que
 * via un ExceptionMapper CDI — pas encore verifie si Cassini honore la
 * decouverte automatique des providers @Provider comme le ferait RESTEasy.
 */
@ApplicationScoped
@Path("/calendrier/evenements")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
public class CalendarResource {

    @Inject
    EventService eventService;

    @Inject
    RecurrenceService recurrenceService;

    @Inject
    HolidayService holidayService;

    @Inject
    QuoteOfTheDayService quoteOfTheDayService;

    @POST
    public Response create(CreateEventRequest request) {
        EventCategory category = request.category() == null ? EventCategory.PERSONNEL : request.category();
        try {
            Event created = eventService.create(new Event(null, request.title(), request.start(), request.end(), category));
            return Response.status(Response.Status.CREATED).entity(EventResponse.from(created)).build();
        } catch (EventConflictException e) {
            return Response.status(Response.Status.CONFLICT).entity(new ErrorPayload(e.getMessage())).build();
        }
    }

    @GET
    public DayViewResponse dayView(@QueryParam("date") String isoDate) {
        LocalDate date = isoDate == null ? LocalDate.now() : LocalDate.parse(isoDate);

        List<EventResponse> events = eventService.findByDate(date).stream()
                .map(EventResponse::from)
                .toList();

        return new DayViewResponse(
                date,
                events,
                holidayService.greetingFor(date),
                quoteOfTheDayService.quoteOfTheDay(date));
    }

    @POST
    @Path("/{id}/recurrence")
    public List<EventResponse> createRecurrence(@PathParam("id") UUID id, RecurrenceRequest request) {
        Event template = eventService.findAll().stream()
                .filter(event -> event.id().equals(id))
                .findFirst()
                .orElseThrow(() -> new NotFoundException("Evenement introuvable : " + id));

        return recurrenceService.generate(template, request.frequency(), request.occurrences()).stream()
                .map(eventService::create)
                .map(EventResponse::from)
                .toList();
    }

    public record ErrorPayload(String message) {
    }
}
