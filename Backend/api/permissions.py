from rest_framework import permissions

class IsAdminOrIsOwner(permissions.BasePermission):
    """
    Allows access only to admin users or to the owner of the object.
    """
    def has_permission(self, request, view):
        # يجب أن يكون المستخدم مسجل دخوله للسماح له بالمرور
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj): # type: ignore
        # المدير العام (is_staff) مسموح له بكل شيء
        if request.user.is_staff:
            return True

        # نسمح بطلبات القراءة الآمنة للجميع (GET, HEAD, OPTIONS)
        # هذا يطبق متطلب "A supplier can read other groceries items"
        if request.method in permissions.SAFE_METHODS:
            return True

        # نتحقق من المالك بناءً على نوع الكائن (Object)
        # إذا كان الكائن هو بقالة
        if hasattr(obj, 'responsible_person'):
            return obj.responsible_person == request.user
        # إذا كان الكائن هو منتج أو دخل يومي
        if hasattr(obj, 'grocery'):
            return obj.grocery.responsible_person == request.user

        return False