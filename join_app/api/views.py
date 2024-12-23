from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ContactSerializer, TaskSerializer, SubtaskSerializer
from ..models import Contact, Task, Subtask

class ContactList(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_guest:
            return self.request.session.get('guest_contacts', [])
        return Contact.objects.filter(user=user)

        if not contacts.filter(email=user.email).exists():
            Contact.objects.create(
                user=user,
                name=user.username,
                email=user.email,
                emblem=user.emblem,
                color=user.color,
                phone="123456789",
            )
        return contacts

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_authenticated and user.is_guest:
            # Gastnutzer speichert Daten nur in der Session
            guest_contacts = self.request.session.get('guest_contacts', [])
            guest_contacts.append(serializer.validated_data)
            self.request.session['guest_contacts'] = guest_contacts
            self.request.session.save()
            print("Kontakt in der Session gespeichert:", guest_contacts)
            return

        # Registrierter Benutzer speichert in der Datenbank
        if not user.is_guest:
            serializer.save(user=user)


class ContactDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_guest:
            return self.request.session.get('guest_contacts', [])
        return Contact.objects.filter(user=self.request.user)


class TaskList(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_guest:
            return self.request.session.get('guest_tasks', [])
        return Task.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_guest:
            guest_tasks = self.request.session.get('guest_tasks', [])
            guest_tasks.append(serializer.validated_data)
            self.request.session['guest_tasks'] = guest_tasks
            self.request.session.save()
        else:
            serializer.save(created_by=self.request.user)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'cardId'

    def get_queryset(self):
        if self.request.user.is_guest:
            return self.request.session.get('guest_tasks', [])
        return Task.objects.filter(created_by=self.request.user)

    def patch(self, request, *args, **kwargs):
        if self.request.user.is_guest:
            return Response({"error": "Guests cannot update tasks partially."}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if 'status' in request.data:
            status_value = request.data.get('status')
            if not status_value:
                return Response(
                    {"error": "Status field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.status = status_value
            instance.save()
            return Response(
                {"message": "Status updated successfully", "status": instance.status}
            )
        return super().partial_update(request, *args, **kwargs)


class SubtaskList(generics.ListCreateAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_guest:
            return self.request.session.get('guest_subtasks', [])
        task = self._get_task()
        return Subtask.objects.filter(task=task)

    def perform_create(self, serializer):
        if self.request.user.is_guest:
            guest_subtasks = self.request.session.get('guest_subtasks', [])
            guest_subtasks.append(serializer.validated_data)
            self.request.session['guest_subtasks'] = guest_subtasks
            self.request.session.save()
        else:
            task = self._get_task()
            serializer.save(task=task)

    def _get_task(self):
        if self.request.user.is_guest:
            return None
        task_id = self.kwargs.get('cardId')
        return get_object_or_404(Task, cardId=task_id, created_by=self.request.user)


class SubtaskDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubtaskSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.is_guest:
            return self.request.session.get('guest_subtasks', [])
        task = self._get_task()
        return Subtask.objects.filter(task=task)

    def patch(self, request, *args, **kwargs):
        if self.request.user.is_guest:
            return Response({"error": "Guests cannot update subtasks partially."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def _get_task(self):
        if self.request.user.is_guest:
            return None
        task_id = self.kwargs.get('cardId')
        return get_object_or_404(Task, cardId=task_id, created_by=self.request.user)
