from planner.models import Course, Core
from scheduleapi.models import Course as Master
from django.shortcuts import render, get_object_or_404
from .forms import CourseForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def get_courses(courses, year, quarter):
    return courses.filter(year=year).filter(quarter=quarter)


@login_required(login_url='/accounts/login/')
def course_list(request):
    curr_user = request.user.id
    courses = Course.objects.filter(user=curr_user)
    context = {
        'years_quarters': sorted({('y%iq%i' % (y, q)): get_courses(courses, y, q) for y in range(1, 5) for q in range(1, 5)}.iteritems()),
        'courses': courses}
    return render(request, 'planner/course_list.html', context)


def course_new(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            try:
                course.user = request.user
                # if it is core
                core = Core.objects.get(fullname=course.fullname)
                # if prereq is fulfilled
                prereq = Course.objects.get(fullname=core.prereq)
            except Core.DoesNotExist:  # if not core
                master = Master.objects.get(fullname=course.fullname)
                course.dept = master.dept
                course.number = master.number
                course.title = master.title
                course.description = master.description
                course.save()
                return redirect('planner.views.course_detail', pk=course.pk)
            else:  # not in master or prereq not fulfilled
                form = CourseForm()
    else:
        form = CourseForm()
    return render(request, 'planner/course_edit.html', {'form': form})


def course_remove(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('planner.views.course_list')


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'planner/course_detail.html', {'course': course})
