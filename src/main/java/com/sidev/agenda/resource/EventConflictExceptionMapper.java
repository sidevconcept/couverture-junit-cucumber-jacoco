package com.sidev.agenda.resource;

import com.sidev.agenda.service.EventConflictException;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;

@Provider
public class EventConflictExceptionMapper implements ExceptionMapper<EventConflictException> {

    @Override
    public Response toResponse(EventConflictException exception) {
        return Response.status(Response.Status.CONFLICT)
                .entity(new ErrorPayload(exception.getMessage()))
                .type(MediaType.APPLICATION_JSON)
                .build();
    }

    public record ErrorPayload(String message) {
    }
}
