package com.sidev.agenda.service;

public class EventConflictException extends RuntimeException {

    public EventConflictException(String message) {
        super(message);
    }
}
